from django.contrib import admin
from .models import ZipName, FileUploadDetail

class ZipNameView(admin.ModelAdmin):
    model = ZipName
    list_display = ('zip_name', 'entry_added_on', 'id')


class FileUploadDetailView(admin.ModelAdmin):
    model = FileUploadDetail
    list_display = ('zip_name', 'file_name', 'session_id', 'offset', 'entry_added_on', 'id' )


admin.site.register(ZipName, ZipNameView)
admin.site.register(FileUploadDetail, FileUploadDetailView)
