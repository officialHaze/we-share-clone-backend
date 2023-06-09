from rest_framework import permissions
import os

admin_key = os.environ.get('ADMIN_KEY')

class AdminTokenPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        admin_token = request.headers.get('Admin-Token')
        if admin_token and admin_token==admin_key:
            return True
        else:
            return False
