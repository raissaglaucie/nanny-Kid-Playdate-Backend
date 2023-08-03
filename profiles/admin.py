from django.contrib import admin

from accounts.models import ModifiedUser
from .models import Profile, Kid, Notification, Comment, Place

admin.site.register(Profile)
admin.site.register(ModifiedUser)
admin.site.register(Kid)
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(Place)
