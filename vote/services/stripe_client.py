"""
Minimal Stripe REST client built on Python's stdlib only (urllib), since
neither the `stripe` package nor `requests` is installed in this project
and installing packages is not this agent's call to make.

NOTE ON VERIFICATION: create_checkout_session() cannot be exercised in this
environment - there is no network egress and no real STRIPE_SECRET_KEY.
The graceful "Stripe non configuré" path (missing key) is what's actually
verified here; the real HTTPS call to api.stripe.com is unverified/best-effort.
verify_webhook_signature(), by contrast, is pure local HMAC computation and
IS fully verified (see the smoke test).
"""

import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
from urllib.parse import urlencode

STRIPE_API_BASE = "https://api.stripe.com/v1"

# How much clock drift to tolerate between the webhook timestamp and now,
# same default as Stripe's own libraries.
WEBHOOK_TOLERANCE_SECONDS = 300


def get_stripe_secret_key():
    return os.getenv('STRIPE_SECRET_KEY') or None


def get_webhook_secret():
    return os.getenv('STRIPE_WEBHOOK_SECRET') or None


def _flatten_for_form(data, prefix=''):
    """Stripe's API expects PHP-style bracket notation for nested params."""
    items = []
    for key, value in data.items():
        form_key = f"{prefix}[{key}]" if prefix else key
        if isinstance(value, dict):
            items.extend(_flatten_for_form(value, form_key))
        elif isinstance(value, (list, tuple)):
            for i, v in enumerate(value):
                if isinstance(v, dict):
                    items.extend(_flatten_for_form(v, f"{form_key}[{i}]"))
                else:
                    items.append((f"{form_key}[{i}]", v))
        elif value is not None:
            items.append((form_key, value))
    return items


class StripeNotConfigured(Exception):
    """Raised when STRIPE_SECRET_KEY isn't set - caller should return a clean 503."""


def create_checkout_session(*, plan, organisation, success_url, cancel_url, customer_email=None):
    """
    Best-effort Stripe Checkout Session creation via a direct HTTPS call to
    Stripe's REST API. Raises StripeNotConfigured if there's no secret key
    (the expected/normal case in this environment), so the view can turn
    that into a clean 503 instead of crashing.
    """
    secret_key = get_stripe_secret_key()
    if not secret_key:
        raise StripeNotConfigured("STRIPE_SECRET_KEY absent")

    payload = {
        'mode': 'subscription',
        'success_url': success_url,
        'cancel_url': cancel_url,
        'line_items': [{
            'quantity': 1,
            'price_data': {
                'currency': plan.currency.lower(),
                'unit_amount': plan.price_cents,
                'recurring': {'interval': 'month'},
                'product_data': {'name': f"Super Vote - {plan.name}"},
            },
        }],
        'metadata': {'organisation_id': str(organisation.id), 'plan_id': str(plan.id)},
    }
    if customer_email:
        payload['customer_email'] = customer_email

    body = urlencode(_flatten_for_form(payload)).encode('utf-8')
    request = urllib.request.Request(
        f"{STRIPE_API_BASE}/checkout/sessions",
        data=body,
        method='POST',
        headers={
            'Authorization': f'Bearer {secret_key}',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    )
    # No egress in this environment: this call is structurally unverifiable
    # here. It's isolated to this one spot so it's obvious what is/isn't tested.
    with urllib.request.urlopen(request, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


def verify_webhook_signature(payload_body: bytes, signature_header: str, secret: str):
    """
    Manual re-implementation of Stripe's webhook signature scheme (stdlib
    hmac/hashlib only, no stripe SDK needed):
    header = "t=<timestamp>,v1=<hex hmac-sha256 of '<timestamp>.<payload>'>"
    Returns True/False. Pure local computation - fully unit-testable.
    """
    if not signature_header:
        return False
    parts = dict(p.split('=', 1) for p in signature_header.split(',') if '=' in p)
    timestamp = parts.get('t')
    signature = parts.get('v1')
    if not timestamp or not signature:
        return False
    if abs(time.time() - int(timestamp)) > WEBHOOK_TOLERANCE_SECONDS:
        return False
    signed_payload = f"{timestamp}.{payload_body.decode('utf-8')}".encode('utf-8')
    expected = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
