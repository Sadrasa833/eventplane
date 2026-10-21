from django.urls import path

from .views import EventParticipantListView, MyRegistrationListCreateView

urlpatterns = [
    path("registrations/", MyRegistrationListCreateView.as_view(), name="my-registrations"),
    path(
        "organizer/events/<int:event_pk>/participants/",
        EventParticipantListView.as_view(),
        name="event-participants",
    ),
]
