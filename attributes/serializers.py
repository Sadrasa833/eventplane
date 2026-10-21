from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import AttributeDefinition, AttributeValue

TYPE_FIELD_MAP = {
    AttributeDefinition.ValueType.TEXT: "value_text",
    AttributeDefinition.ValueType.NUMBER: "value_number",
    AttributeDefinition.ValueType.BOOLEAN: "value_boolean",
    AttributeDefinition.ValueType.DATE: "value_date",
}


class AttributeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeDefinition
        fields = ["id", "key", "label", "value_type", "applies_to", "description"]


class AttributeValueSerializer(serializers.ModelSerializer):
    """
    Exposes a single 'value' field to API clients and internally routes it
    to the correct type-safe column based on the attribute's value_type.
    """

    attribute_key = serializers.CharField(source="attribute.key", read_only=True)
    value = serializers.SerializerMethodField()
    input_value = serializers.CharField(write_only=True, source="_raw_value")

    class Meta:
        model = AttributeValue
        fields = ["id", "attribute", "attribute_key", "value", "input_value"]

    def get_value(self, obj):
        return obj.value

    def _coerce(self, attribute, raw_value):
        field = TYPE_FIELD_MAP[attribute.value_type]
        if attribute.value_type == AttributeDefinition.ValueType.BOOLEAN:
            coerced = str(raw_value).strip().lower() in ("1", "true", "yes")
        elif attribute.value_type == AttributeDefinition.ValueType.NUMBER:
            try:
                coerced = float(raw_value)
            except (TypeError, ValueError):
                raise serializers.ValidationError({"input_value": "Must be a number."})
        else:
            coerced = raw_value
        return field, coerced

    @staticmethod
    def _full_clean(instance):
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            )

    def create(self, validated_data):
        raw_value = validated_data.pop("_raw_value")
        attribute = validated_data["attribute"]
        field, coerced = self._coerce(attribute, raw_value)
        validated_data[field] = coerced
        instance = AttributeValue(**validated_data)
        self._full_clean(instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        raw_value = validated_data.pop("_raw_value", None)
        if raw_value is not None:
            field, coerced = self._coerce(instance.attribute, raw_value)
            for f in TYPE_FIELD_MAP.values():
                setattr(instance, f, None)
            setattr(instance, field, coerced)
        self._full_clean(instance)
        instance.save()
        return instance
