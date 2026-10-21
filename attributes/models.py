from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models


class AttributeDefinition(models.Model):

    class ValueType(models.TextChoices):
        TEXT = "text", "Text"
        NUMBER = "number", "Number"
        BOOLEAN = "boolean", "Boolean"
        DATE = "date", "Date"

    class AppliesTo(models.TextChoices):
        EVENT = "event", "Event"
        STAGE = "stage", "Stage"

    key = models.SlugField(max_length=100, unique=True)
    label = models.CharField(max_length=150)
    value_type = models.CharField(max_length=10, choices=ValueType.choices)
    applies_to = models.CharField(max_length=10, choices=AppliesTo.choices)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.key} ({self.value_type}, for {self.applies_to})"


class AttributeValue(models.Model):
    """
    EAV "value": the concrete, type-safe value of one AttributeDefinition
    for one specific Event or Stage (via a generic relation, restricted to
    those two models in clean()). Exactly one of the typed value_* fields
    is populated, matching the definition's value_type.
    """

    attribute = models.ForeignKey(
        AttributeDefinition, on_delete=models.CASCADE, related_name="values"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    owner = GenericForeignKey("content_type", "object_id")

    value_text = models.CharField(max_length=500, null=True, blank=True)
    value_number = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "content_type", "object_id"],
                name="unique_attribute_value_per_owner",
            )
        ]

    def clean(self):
        allowed_models = {"event": "event", "stage": "stage"}
        model_name = self.content_type.model
        if model_name not in allowed_models:
            raise ValidationError("Attribute values can only attach to an Event or a Stage.")
        if model_name != self.attribute.applies_to:
            raise ValidationError(
                f"Attribute '{self.attribute.key}' applies to '{self.attribute.applies_to}', "
                f"not '{model_name}'."
            )
        populated = [
            v for v in (self.value_text, self.value_number, self.value_boolean, self.value_date)
            if v is not None
        ]
        if len(populated) != 1:
            raise ValidationError("Exactly one typed value field must be set.")

    @property
    def value(self):
        return next(
            v for v in (self.value_text, self.value_number, self.value_boolean, self.value_date)
            if v is not None
        )

    def __str__(self):
        return f"{self.attribute.key}={self.value} on {self.owner}"
