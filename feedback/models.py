from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from events.models import Event
from registrations.models import Registration


class Feedback(models.Model):
    registration = models.OneToOneField(
        Registration, on_delete=models.CASCADE, related_name="feedback"
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.registration.event.status != Event.Status.FINISHED:
            raise ValidationError("Feedback can only be submitted once the event is Finished.")
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")

    def __str__(self):
        return f"Feedback by {self.registration.participant} on {self.registration.event}"


class Result(models.Model):

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="result")
    published_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True)

    def clean(self):
        if self.event.status != Event.Status.FINISHED:
            raise ValidationError("Results can only be created for a Finished event.")

    def __str__(self):
        return f"Results for {self.event}"


class ResultEntry(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="entries")
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(null=True, blank=True)
    score = models.CharField(max_length=100, blank=True)
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return f"{self.participant} — rank {self.rank}"
