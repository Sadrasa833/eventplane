from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AttributeDefinitionViewSet,
    EventAttributeValueView,
    StageAttributeValueView,
)

router = DefaultRouter()
router.register("attribute-definitions", AttributeDefinitionViewSet, basename="attribute-definition")

urlpatterns = [
    *router.urls,
    path(
        "organizer/events/<int:event_pk>/attributes/",
        EventAttributeValueView.as_view(),
        name="event-attributes",
    ),
    path(
        "organizer/stages/<int:stage_pk>/attributes/",
        StageAttributeValueView.as_view(),
        name="stage-attributes",
    ),
]
