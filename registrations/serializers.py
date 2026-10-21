from rest_framework import serializers

from .models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "event", "event_title", "participant", "status", "registered_at"]
        read_only_fields = ["participant", "status", "registered_at"]

    def validate_event(self, event):
        from events.models import Event

        if event.status != Event.Status.PUBLISHED:
            raise serializers.ValidationError("Only Published events accept registrations.")
        if not event.has_capacity:
            raise serializers.ValidationError("This event is at full capacity.")
        return event

    def validate(self, attrs):
        request = self.context["request"]
        if Registration.objects.filter(participant=request.user, event=attrs["event"]).exists():
            raise serializers.ValidationError("You are already registered for this event.")
        return attrs

    def create(self, validated_data):
        validated_data["participant"] = self.context["request"].user
        return super().create(validated_data)


class ParticipantSummarySerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(source="participant.username", read_only=True)
    participant_email = serializers.CharField(source="participant.email", read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "participant", "participant_username", "participant_email", "status", "registered_at"]
