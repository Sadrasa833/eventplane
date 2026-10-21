from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ORGANIZER = "organizer", "Organizer"
        PARTICIPANT = "participant", "Participant"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARTICIPANT)

    @property
    def is_organizer(self):
        return self.role == self.Role.ORGANIZER

    @property
    def is_participant(self):
        return self.role == self.Role.PARTICIPANT

    def __str__(self):
        return f"{self.username} ({self.role})"
