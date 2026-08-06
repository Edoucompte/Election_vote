"""
Plan-quota enforcement for organisation-scoped resources (elections,
electors). Kept as small, reusable, dependency-free helpers so the call
sites in the shared views1/*.py files only need a single early-return
guard clause each.
"""

from vote.models.subscription import Subscription


def get_active_subscription(organisation):
    if organisation is None:
        return None
    return Subscription.objects.filter(organisation=organisation).select_related('plan').first()


def check_election_quota(organisation):
    """
    Returns None if the organisation is still under its plan's election
    quota (or has no subscription/plan at all, in which case we fail open
    rather than break orgs the auto-provisioning signal/backfill missed),
    otherwise a French, user-facing error message.
    """
    subscription = get_active_subscription(organisation)
    if subscription is None or subscription.plan is None:
        return None

    from vote.models import Election  # local import: avoids a models-init cycle

    limit = subscription.plan.max_elections
    used = Election.objects.filter(organisation=organisation).count()
    if used >= limit:
        return f"Limite du plan atteinte ({limit} élections max)."
    return None


def check_elector_quota(organisation, additional=1):
    """
    Same as check_election_quota, but for the number of electors about to
    be added (additional lets a mass-import check the whole batch at once).
    """
    subscription = get_active_subscription(organisation)
    if subscription is None or subscription.plan is None:
        return None

    from vote.models import CustomUser  # local import: avoids a models-init cycle

    limit = subscription.plan.max_electors
    used = CustomUser.objects.filter(organisation=organisation, is_elector=True).count()
    if used + additional > limit:
        return f"Limite du plan atteinte ({limit} électeurs max)."
    return None
