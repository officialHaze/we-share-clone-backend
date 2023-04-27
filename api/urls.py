from django.urls import path, include

urlpatterns = [
    path('file/', include('files.urls')),
]