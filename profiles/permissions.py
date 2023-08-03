from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import APIException

from rest_framework import status
from profiles.models import Profile


class IsProfileOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, 'profile'):
            profile = get_object_or_404(Profile, id=view.profile.id)
            if profile.owner_id != request.user.id:
                raise NotProfileOwner()
        return super().has_permission(request, view)


class NotProfileOwner(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {'detail': 'Not profile owner'}
