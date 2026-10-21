from django.contrib import admin

from .models import Event, Stage, StageRoleAssignment

admin.site.register(Event)
admin.site.register(Stage)
admin.site.register(StageRoleAssignment)
