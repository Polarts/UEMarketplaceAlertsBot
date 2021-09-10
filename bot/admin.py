from django.contrib import admin

from .models import AssetSource, Asset, LogEntry

admin.site.register(AssetSource)
admin.site.register(Asset)
admin.site.register(LogEntry)
