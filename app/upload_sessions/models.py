from django.db import models
from django.utils.translation import gettext_lazy as _


class ZipName(models.Model):
    zip_name = models.TextField(_('Zip Name'))
    entry_added_on = models.DateTimeField(_('Entry added on'), auto_now_add=True)

    def __str__(self):
        return self.zip_name
    

class FileUploadDetail(models.Model):
    zip_name = models.ForeignKey(ZipName, on_delete=models.CASCADE)
    file_name = models.TextField(_('File name'))
    session_id = models.TextField(_('Upload Session ID'))
    offset = models.IntegerField(_('Offset'))
    entry_added_on = models.DateTimeField(_('Entry added on'), auto_now_add=True)

    def __str__(self):
        return self.file_name
