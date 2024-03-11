from django.contrib import admin
from django.apps import apps
from django.contrib.admin.models import LogEntry

# Register your models here.
# admin.site.register(LogEntry)
models = apps.get_containing_app_config("main").get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
