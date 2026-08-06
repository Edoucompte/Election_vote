from django.conf import settings
from django.db import models


class Organisation(models.Model):
    """
    Un compte (organisation) qui possède ses propres élections, électeurs et
    superviseurs, entièrement cloisonnés de ceux des autres organisations.
    """

    name = models.CharField(max_length=150)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_organisations',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
