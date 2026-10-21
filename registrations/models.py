from django.conf import settings
from django.db import models

from events.models import Event


class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "event"], name="unique_registration_per_participant_event"
            )
        ]
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.participant} -> {self.event} ({self.status})"
