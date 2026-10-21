from rest_framework import serializers

from common.serializers import FullCleanModelSerializer

from .models import Event, Stage, StageRoleAssignment


class StageRoleAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageRoleAssignment
        fields = ["id", "stage", "user", "role_type", "note"]
        read_only_fields = ["stage"]


class StageSerializer(FullCleanModelSerializer):
    role_assignments = StageRoleAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = [
            "id", "event", "title", "description", "order",
            "start_time", "end_time", "role_assignments",
        ]
        read_only_fields = ["event"]


class EventPublicSerializer(serializers.ModelSerializer):
    """What Participants / anonymous visitors see."""

    stages = StageSerializer(many=True, read_only=True)
    spots_left = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "title", "description", "start_time", "end_time",
            "capacity", "status", "stages", "spots_left",
        ]

    def get_spots_left(self, obj):
        return max(obj.capacity - obj.confirmed_registration_count, 0)


class EventOrganizerSerializer(FullCleanModelSerializer):
    """Full read/write serializer for the owning organizer."""

    stages = StageSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "organizer", "title", "description", "start_time", "end_time",
            "capacity", "status", "stages", "created_at", "updated_at",
        ]
        read_only_fields = ["organizer", "status", "created_at", "updated_at"]


class EventStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Event.Status.choices)
