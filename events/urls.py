from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    EventStatusUpdateView,
    OrganizerEventViewSet,
    PublicEventDetailView,
    PublicEventListView,
    StageRoleAssignmentViewSet,
    StageViewSet,
)

router = DefaultRouter()
router.register("organizer/events", OrganizerEventViewSet, basename="organizer-event")

stages_router = NestedDefaultRouter(router, "organizer/events", lookup="event")
stages_router.register("stages", StageViewSet, basename="event-stages")

roles_router = NestedDefaultRouter(stages_router, "stages", lookup="stage")
roles_router.register("roles", StageRoleAssignmentViewSet, basename="stage-roles")

urlpatterns = [
    *router.urls,
    *stages_router.urls,
    *roles_router.urls,
]

# path-style additions (not covered by routers)
from django.urls import path  # noqa: E402

urlpatterns += [
    path("public/events/", PublicEventListView.as_view(), name="public-event-list"),
    path("public/events/<int:pk>/", PublicEventDetailView.as_view(), name="public-event-detail"),
    path(
        "organizer/events/<int:pk>/status/",
        EventStatusUpdateView.as_view(),
        name="event-status-update",
    ),
]
