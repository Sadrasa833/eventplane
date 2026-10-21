from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class FullCleanModelSerializer(serializers.ModelSerializer):
    """
    DRF's default create()/update() call Model.objects.create() / .save()
    directly — they do NOT run Model.full_clean(), so any validation
    written in a model's clean() method (state-machine checks, cross-field
    rules, etc.) is silently skipped unless we call it explicitly here.
    This base class runs full_clean() on create/update and turns a Django
    ValidationError into a DRF one (400 with a normal error body) instead
    of letting it bubble up as an unhandled 500.
    """

    def _full_clean(self, instance):
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        self._full_clean(instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        self._full_clean(instance)
        instance.save()
        return instance
