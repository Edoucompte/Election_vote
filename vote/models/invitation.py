import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_invitation_token():
    return secrets.token_urlsafe(32)


def default_invitation_expiration():
    return timezone.now() + timezone.timedelta(days=7)


class Invitation(models.Model):
    """Invite sent by a supervisor for an email to join their org as a co-supervisor."""

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_EXPIRED = 'expired'
    STATUS_REVOKED = 'revoked'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_ACCEPTED, 'Acceptée'),
        (STATUS_EXPIRED, 'Expirée'),
        (STATUS_REVOKED, 'Révoquée'),
    ]

    organisation = models.ForeignKey(
        'vote.Organisation',
        on_delete=models.CASCADE,
        related_name='invitations',
    )
    email = models.EmailField()
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_invitations',
    )
    token = models.CharField(max_length=64, unique=True, default=generate_invitation_token)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_invitation_expiration)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invitation {self.email} -> organisation {self.organisation_id} ({self.status})"

    def is_expired(self):
        return timezone.now() >= self.expires_at
