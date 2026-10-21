from django.urls import path

from .views import (
    EventFeedbackListView,
    MyFeedbackCreateView,
    PublicResultDetailView,
    ResultPublishView,
)

urlpatterns = [
    path("feedback/", MyFeedbackCreateView.as_view(), name="submit-feedback"),
    path(
        "organizer/events/<int:event_pk>/feedback/",
        EventFeedbackListView.as_view(),
        name="event-feedback",
    ),
    path(
        "organizer/events/<int:event_pk>/results/",
        ResultPublishView.as_view(),
        name="publish-results",
    ),
    path(
        "public/events/<int:event_pk>/results/",
        PublicResultDetailView.as_view(),
        name="public-results",
    ),
]
