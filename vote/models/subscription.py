from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from vote.models.organisation import Organisation

# Trial length granted to a brand new organisation on the default plan.
DEFAULT_TRIAL_DAYS = 14


class Plan(models.Model):
    """
    A billing plan: what an organisation is allowed to use, and how much it
    costs. Plans are managed via the admin / seeded via migration, not via a
    public API in this pass.
    """

    name = models.CharField(max_length=100, unique=True)
    # Amount in the smallest unit of `currency` (e.g. cents), to avoid float
    # rounding issues. Default currency is XOF (West African CFA franc) since
    # the product targets francophone West Africa; no provider decision was
    # requested here, this is just a sensible default.
    price_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default='XOF')
    max_elections = models.PositiveIntegerField()
    max_electors = models.PositiveIntegerField()
    max_candidatures_per_election = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price_cents', 'id']

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    One active subscription per organisation. Auto-created (trialing, on the
    cheapest active plan) whenever a new Organisation is saved for the first
    time - see the post_save receiver below.
    """

    STATUS_CHOICES = [
        ('trialing', 'Essai'),
        ('active', 'Actif'),
        ('past_due', 'Impayé'),
        ('canceled', 'Annulé'),
    ]

    organisation = models.OneToOneField(
        Organisation, on_delete=models.CASCADE, related_name='subscription'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    # TODO: mobile money provider not chosen yet (MonCash only floated as an
    # example, never confirmed) - field unused until a provider is decided.
    mobile_money_reference = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organisation.name} - {self.plan.name} ({self.status})"


def default_plan():
    """The plan a brand new organisation is enrolled on: cheapest active plan."""
    return Plan.objects.filter(is_active=True).order_by('price_cents', 'id').first()


@receiver(post_save, sender=Organisation, dispatch_uid='vote_create_default_subscription')
def create_default_subscription(sender, instance, created, **kwargs):
    """
    New organisations get a trialing subscription on the default plan for
    free, automatically - regardless of which view/flow created them
    (existing bootstrap in CustomUserView.post, a future signup flow, the
    admin, django_seed...). Kept as a signal on Organisation (not a call in
    the view) precisely so it doesn't require touching shared view files.
    """
    if not created:
        return
    if hasattr(instance, 'subscription'):
        return
    plan = default_plan()
    if plan is None:
        # No plan seeded yet (e.g. fresh DB before the seed migration ran).
        return
    now = timezone.now()
    Subscription.objects.create(
        organisation=instance,
        plan=plan,
        status='trialing',
        current_period_start=now,
        current_period_end=now + timedelta(days=DEFAULT_TRIAL_DAYS),
    )
