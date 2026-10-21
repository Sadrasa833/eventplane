from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from events.models import Event
from events.permissions import IsOrganizer
from registrations.models import Registration

from .models import Feedback, Result
from .serializers import FeedbackSerializer, ResultSerializer


class MyFeedbackCreateView(generics.CreateAPIView):

    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventFeedbackListView(generics.ListAPIView):

    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs["event_pk"], organizer=self.request.user)
        return Feedback.objects.filter(registration__event=event)


class ResultPublishView(generics.CreateAPIView):

    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def perform_create(self, serializer):
        event = get_object_or_404(
            Event, pk=self.kwargs["event_pk"], organizer=self.request.user
        )
        serializer.save(event=event)


class PublicResultDetailView(generics.RetrieveAPIView):

    serializer_class = ResultSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Result.objects.exclude(published_at__isnull=True)
    lookup_field = "event_id"
    lookup_url_kwarg = "event_pk"
