import json

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import response, status
from rest_framework.views import APIView

from vote.models import CustomUser, Election, Plan
from vote.services import stripe_client
from vote.services.quota import get_active_subscription
from vote.views1.user import CustomAuthentication, res


class OrganisationSubscriptionView(APIView):
    """GET /organisations/me/subscription/ - plan, status and usage vs. limits."""

    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(operation_description="Current subscription and usage for the connected org", responses=res)
    def get(self, request):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        organisation = request.user.organisation
        subscription = get_active_subscription(organisation)
        if subscription is None:
            return response.Response({
                "succes": False,
                "errors": "Aucun abonnement trouvé pour cette organisation."
            }, status=status.HTTP_404_NOT_FOUND)

        plan = subscription.plan
        elections_used = Election.objects.filter(organisation=organisation).count()
        electors_used = CustomUser.objects.filter(organisation=organisation, is_elector=True).count()

        return response.Response({
            "succes": True,
            "details": "Abonnement de l'organisation",
            "data": {
                "plan": plan.name,
                "status": subscription.status,
                "currency": plan.currency,
                "price_cents": plan.price_cents,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "elections_used": elections_used,
                "elections_limit": plan.max_elections,
                "electors_used": electors_used,
                "electors_limit": plan.max_electors,
                "max_candidatures_per_election": plan.max_candidatures_per_election,
            }
        }, status=status.HTTP_200_OK)


class SubscriptionCheckoutView(APIView):
    """
    POST /organisations/me/subscription/checkout/ - builds a Stripe Checkout
    Session. UNVERIFIED beyond the "no key configured" path: see
    vote/services/stripe_client.py docstring - there is no network egress
    and no real STRIPE_SECRET_KEY in this environment.
    """

    authentication_classes = [CustomAuthentication]

    @swagger_auto_schema(
        operation_description="Create a Stripe Checkout session for a plan upgrade",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'plan_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="target plan id"),
                'success_url': openapi.Schema(type=openapi.TYPE_STRING),
                'cancel_url': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['plan_id'],
        ),
        responses=res,
    )
    def post(self, request):
        if not (request.user.is_authenticated and request.user.is_supervisor):
            return response.Response({"details": "Access denied", "succes": False}, status=status.HTTP_403_FORBIDDEN)

        if not stripe_client.get_stripe_secret_key():
            return response.Response({
                "succes": False,
                "errors": "Stripe non configuré."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        plan = Plan.objects.filter(pk=request.data.get('plan_id'), is_active=True).first()
        if plan is None:
            return response.Response({"succes": False, "errors": "Plan introuvable."}, status=status.HTTP_400_BAD_REQUEST)

        success_url = request.data.get('success_url') or 'http://localhost:5173/billing/success'
        cancel_url = request.data.get('cancel_url') or 'http://localhost:5173/billing/cancel'

        try:
            session = stripe_client.create_checkout_session(
                plan=plan,
                organisation=request.user.organisation,
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=request.user.email,
            )
        except stripe_client.StripeNotConfigured:
            return response.Response({"succes": False, "errors": "Stripe non configuré."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Network/API failure: never crash the endpoint, report cleanly instead.
            print("Stripe checkout session creation failed:", e)
            return response.Response({
                "succes": False,
                "errors": "Impossible de contacter Stripe pour le moment."
            }, status=status.HTTP_502_BAD_GATEWAY)

        return response.Response({
            "succes": True,
            "details": "Session de paiement créée",
            "data": {"checkout_url": session.get('url'), "session_id": session.get('id')},
        }, status=status.HTTP_201_CREATED)


class StripeWebhookView(APIView):
    """
    POST /webhooks/stripe/ (mounted at /api/v1/webhooks/stripe/, same prefix
    as every other endpoint in this project). No auth: Stripe calls this
    directly and authenticates via the signature header instead.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload_body = request.body
        secret = stripe_client.get_webhook_secret()
        signature_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        if secret:
            if not stripe_client.verify_webhook_signature(payload_body, signature_header, secret):
                return response.Response({"succes": False, "errors": "Signature invalide."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("WARNING: STRIPE_WEBHOOK_SECRET is not set - processing webhook without signature verification (insecure).")

        try:
            event = json.loads(payload_body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return response.Response({"succes": False, "errors": "Payload JSON invalide."}, status=status.HTTP_400_BAD_REQUEST)

        event_type = event.get('type')
        data_object = (event.get('data') or {}).get('object') or {}
        handled = _handle_stripe_event(event_type, data_object)

        # Always 2xx for a well-formed event: Stripe retries indefinitely
        # otherwise, and there's nothing more it can do if we can't match it.
        return response.Response({
            "succes": True,
            "details": f"Événement {event_type} {'traité' if handled else 'ignoré'}",
        }, status=status.HTTP_200_OK)


def _find_subscription_for_event(data_object):
    from vote.models import Subscription

    organisation_id = (data_object.get('metadata') or {}).get('organisation_id')
    if organisation_id:
        sub = Subscription.objects.filter(organisation_id=organisation_id).first()
        if sub:
            return sub

    customer_id = data_object.get('customer')
    if customer_id:
        sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
        if sub:
            return sub

    subscription_id = data_object.get('subscription') or data_object.get('id')
    if subscription_id:
        return Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
    return None


def _handle_stripe_event(event_type, data_object):
    subscription = _find_subscription_for_event(data_object)
    if subscription is None:
        print(f"Stripe webhook: no local Subscription matched for event {event_type}")
        return False

    if event_type == 'checkout.session.completed':
        subscription.status = 'active'
        if data_object.get('customer'):
            subscription.stripe_customer_id = data_object.get('customer')
        if data_object.get('subscription'):
            subscription.stripe_subscription_id = data_object.get('subscription')
        subscription.save(update_fields=['status', 'stripe_customer_id', 'stripe_subscription_id', 'updated_at'])
        return True

    if event_type == 'invoice.payment_failed':
        subscription.status = 'past_due'
        subscription.save(update_fields=['status', 'updated_at'])
        return True

    if event_type == 'customer.subscription.deleted':
        subscription.status = 'canceled'
        subscription.save(update_fields=['status', 'updated_at'])
        return True

    return False
