from django.contrib import admin
from django.urls import path, include, re_path
from .views import redirect_to_long_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    re_path(r'(?P<id>\w+)/$', redirect_to_long_url),
]
