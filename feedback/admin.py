from django.contrib import admin

from .models import Feedback, Result, ResultEntry

admin.site.register(Feedback)
admin.site.register(Result)
admin.site.register(ResultEntry)
