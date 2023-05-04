from django.contrib import admin
from django.urls import path, include, re_path
from .views import redirect_to_long_url, connection_stream

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', connection_stream),
    re_path(r'(?P<id>\w+)/$', redirect_to_long_url),
]
