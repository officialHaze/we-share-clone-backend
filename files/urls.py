from django.urls import path, re_path
from . import views

urlpatterns = [
    path('upload/', views.upload_file),
    re_path(r'^download/(?P<id>\w+)/$', views.get_download_url),
    re_path('shorten_url/', views.shorten_url),
]