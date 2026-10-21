from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets

from events.models import Event, Stage
from events.permissions import IsOrganizer

from .models import AttributeDefinition, AttributeValue
from .serializers import AttributeDefinitionSerializer, AttributeValueSerializer


class AttributeDefinitionViewSet(viewsets.ModelViewSet):
  
    queryset = AttributeDefinition.objects.all()
    serializer_class = AttributeDefinitionSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOrganizer()]


class BaseAttributeValueView(generics.ListCreateAPIView):
    serializer_class = AttributeValueSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]
    owner_model = None
    owner_kwarg = None

    def get_owner(self):
        owner = get_object_or_404(self.owner_model, pk=self.kwargs[self.owner_kwarg])
        event = owner if self.owner_model is Event else owner.event
        if event.organizer_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this event.")
        return owner

    def get_queryset(self):
        owner = self.get_owner()
        ct = ContentType.objects.get_for_model(owner)
        return AttributeValue.objects.filter(content_type=ct, object_id=owner.id)

    def perform_create(self, serializer):
        owner = self.get_owner()
        ct = ContentType.objects.get_for_model(owner)
        serializer.save(content_type=ct, object_id=owner.id)


class EventAttributeValueView(BaseAttributeValueView):
    owner_model = Event
    owner_kwarg = "event_pk"


class StageAttributeValueView(BaseAttributeValueView):
    owner_model = Stage
    owner_kwarg = "stage_pk"
