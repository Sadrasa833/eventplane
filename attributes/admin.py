from django.contrib import admin

from .models import AttributeDefinition, AttributeValue

admin.site.register(AttributeDefinition)
admin.site.register(AttributeValue)
