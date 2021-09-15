from django.contrib import admin

from .models import AssetSource, Asset

admin.site.register(AssetSource)
admin.site.register(Asset)
