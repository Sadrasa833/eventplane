from rest_framework import serializers

from common.serializers import FullCleanModelSerializer

from .models import Feedback, Result, ResultEntry


class FeedbackSerializer(FullCleanModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "registration", "rating", "comment", "created_at"]
        read_only_fields = ["created_at"]

    def validate_registration(self, registration):
        request = self.context["request"]
        if registration.participant_id != request.user.id:
            raise serializers.ValidationError("You can only give feedback on your own registration.")
        return registration


class ResultEntrySerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(source="participant.username", read_only=True)

    class Meta:
        model = ResultEntry
        fields = ["id", "participant", "participant_username", "rank", "score", "details"]


class ResultSerializer(FullCleanModelSerializer):
    entries = ResultEntrySerializer(many=True)

    class Meta:
        model = Result
        fields = ["id", "event", "published_at", "summary", "entries"]
        read_only_fields = ["event", "published_at"]

    def create(self, validated_data):
        entries_data = validated_data.pop("entries")
        from django.utils import timezone

        result = Result(**validated_data)
        self._full_clean(result)
        result.published_at = timezone.now()
        result.save()
        for entry in entries_data:
            ResultEntry.objects.create(result=result, **entry)
        return result
