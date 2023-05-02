from django.contrib import admin
from .models import File, ShortURL


class FileAdminView(admin.ModelAdmin):
    model = File
    list_display = ('file_name', File.short_description, 'file', 'uploaded_on', 'expires_on', 'id')


class ShortURLAdminView(admin.ModelAdmin):
    model = ShortURL
    list_display = ('id', 'long_url', 'short_url', 'visited', 'created')


admin.site.register(File, FileAdminView)
admin.site.register(ShortURL, ShortURLAdminView)
