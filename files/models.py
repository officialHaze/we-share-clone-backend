from django.db import models
from django.utils.translation import gettext_lazy as _


class File(models.Model):
    file_name = models.CharField(_('Name'), max_length=100)
    file_description = models.TextField(_('Description'), max_length=300)
    file = models.CharField(_('Download URL'), max_length=500)
    uploaded_on = models.DateTimeField(_('Uploaded on'), auto_now_add=True)
    expires_on = models.CharField(_('Expires on'), max_length=100)

    def short_description(self):
        return self.file_description[:50]

    def __str__(self):
        return self.file_name


class ShortURL(models.Model):
    id = models.CharField(_('URL Id'), max_length=8, primary_key=True)
    long_url = models.TextField(_('Long URL'))
    short_url = models.TextField(_('Short URL'))
    visited = models.IntegerField(_('Visitors'), default=0)
    created = models.DateTimeField(_('Created on'), auto_now_add=True)

    def __str__(self):
        return self.id
