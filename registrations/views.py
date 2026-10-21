from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from events.models import Event
from events.permissions import IsOrganizer

from .models import Registration
from .serializers import ParticipantSummarySerializer, RegistrationSerializer


class MyRegistrationListCreateView(generics.ListCreateAPIView):

    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(participant=self.request.user)


class EventParticipantListView(generics.ListAPIView):

    serializer_class = ParticipantSummarySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs["event_pk"], organizer=self.request.user)
        return Registration.objects.filter(event=event)
