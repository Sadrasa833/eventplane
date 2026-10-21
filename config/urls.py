from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("events.urls")),
    path("api/", include("attributes.urls")),
    path("api/", include("registrations.urls")),
    path("api/", include("feedback.urls")),
]
