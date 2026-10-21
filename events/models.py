from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Event(models.Model):
    """
    An event owned by an Organizer. Registration and capacity are handled
    at the Event level (not per-Stage) — see README "Architecture
    decisions" for the reasoning. Stages are sub-sessions used to organize
    the event's schedule and role assignments (speakers/judges/mentors),
    not separate registration units.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"
        FINISHED = "finished", "Finished"

    # Forward-only state machine, enforced in save()/clean().
    ALLOWED_TRANSITIONS = {
        Status.DRAFT: {Status.PUBLISHED},
        Status.PUBLISHED: {Status.CLOSED},
        Status.CLOSED: {Status.FINISHED},
        Status.FINISHED: set(),
    }

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.title} [{self.status}]"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("end_time must be after start_time.")

    def transition_to(self, new_status):
        """Enforce the event lifecycle's legal transitions."""
        if new_status == self.status:
            return
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValidationError(
                f"Cannot transition event from '{self.status}' to '{new_status}'."
            )
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])

    @property
    def confirmed_registration_count(self):
        return self.registrations.filter(status="confirmed").count()

    @property
    def has_capacity(self):
        return self.confirmed_registration_count < self.capacity


class Stage(models.Model):
    """
    A stage/session/round belonging to one Event, with its own order and
    time window and independent info. Capacity/registration stay at the
    Event level by design (see README).
    """

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="stages")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ["event", "order"]
        constraints = [
            models.UniqueConstraint(fields=["event", "order"], name="unique_stage_order_per_event")
        ]

    def __str__(self):
        return f"{self.event.title} — Stage {self.order}: {self.title}"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("end_time must be after start_time.")


class StageRoleAssignment(models.Model):
    """A person assigned to a stage-specific role (speaker, judge, mentor, ...)."""

    class RoleType(models.TextChoices):
        SPEAKER = "speaker", "Speaker"
        JUDGE = "judge", "Judge"
        MENTOR = "mentor", "Mentor"
        OTHER = "other", "Other"

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="role_assignments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stage_roles"
    )
    role_type = models.CharField(max_length=20, choices=RoleType.choices)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["stage", "user", "role_type"], name="unique_role_per_stage_user"
            )
        ]

    def __str__(self):
        return f"{self.user} as {self.role_type} on {self.stage}"
