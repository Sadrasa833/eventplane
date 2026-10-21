from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, Stage, StageRoleAssignment
from .permissions import IsEventOwner, IsOrganizer, IsStageEventOwner
from .serializers import (
    EventOrganizerSerializer,
    EventPublicSerializer,
    EventStatusUpdateSerializer,
    StageRoleAssignmentSerializer,
    StageSerializer,
)


# ---------- Public APIs ----------

class PublicEventListView(generics.ListAPIView):
    """Public: list only Published events."""

    serializer_class = EventPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Event.objects.filter(status=Event.Status.PUBLISHED)


class PublicEventDetailView(generics.RetrieveAPIView):
    """Public: view details of a Published event."""

    serializer_class = EventPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Event.objects.filter(status=Event.Status.PUBLISHED)


# ---------- Organizer APIs ----------

class OrganizerEventViewSet(viewsets.ModelViewSet):
    """Organizer: create/list/retrieve/update their own events."""

    serializer_class = EventOrganizerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOrganizer(), IsEventOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventStatusUpdateView(APIView):
    """Organizer: transition an event's status following the legal state machine."""

    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def patch(self, request, pk):
        from rest_framework.exceptions import PermissionDenied

        event = get_object_or_404(Event, pk=pk)
        if not IsEventOwner().has_object_permission(request, self, event):
            raise PermissionDenied("You do not own this event.")
        serializer = EventStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            event.transition_to(serializer.validated_data["status"])
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message)
        return Response(EventOrganizerSerializer(event).data)


class StageViewSet(viewsets.ModelViewSet):
    """Organizer: manage stages belonging to their own events."""

    serializer_class = StageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return Stage.objects.filter(event__organizer=self.request.user, event_id=self.kwargs["event_pk"])

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOrganizer(), IsStageEventOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs["event_pk"], organizer=self.request.user)
        serializer.save(event=event)


class StageRoleAssignmentViewSet(viewsets.ModelViewSet):
    """Organizer: assign speakers/judges/mentors to a stage."""

    serializer_class = StageRoleAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return StageRoleAssignment.objects.filter(
            stage__event__organizer=self.request.user, stage_id=self.kwargs["stage_pk"]
        )

    def perform_create(self, serializer):
        stage = get_object_or_404(
            Stage, pk=self.kwargs["stage_pk"], event__organizer=self.request.user
        )
        serializer.save(stage=stage)
