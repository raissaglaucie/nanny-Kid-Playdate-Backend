from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import ModifiedUser



class Profile(models.Model):
    owner = models.OneToOneField(to=ModifiedUser, related_name='profile_owner', on_delete=models.CASCADE)

    followers = models.ManyToManyField(to=ModifiedUser, related_name="profile_followers", blank=True)

    name = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    phone_num = PhoneNumberField(null=False, blank=False, unique=False)
    likes = models.ManyToManyField(to=ModifiedUser, related_name="profile_likes", blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)



class Comment(models.Model):
    user = models.ForeignKey(to=ModifiedUser, related_name='comment', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True)
    profile = models.ForeignKey(to=Profile, related_name='ptofile_comment', on_delete=models.CASCADE)
    contents = models.CharField(max_length=250)



class Place(models.Model):
    profile = models.ForeignKey(to=Profile, related_name='profile', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    place_pic = models.ImageField(upload_to='places/', null=True, blank=True)
    contents = models.CharField(max_length=5000)
    publish_timestamp = models.DateTimeField(auto_created=True, auto_now_add=True)
    likes = models.ManyToManyField(to=ModifiedUser, related_name="place_likes")


class Kid(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    age = models.DecimalField(max_digits=3, decimal_places=0, validators=[MinValueValidator(0)])
    picture = models.ImageField(upload_to='kids/', null=True, blank=True)
    profile = models.ForeignKey(to=Profile, on_delete=models.CASCADE, related_name='kids')



class Notification(models.Model):
    user = models.ForeignKey(to=ModifiedUser, on_delete=models.CASCADE, related_name='users')
    # Enum, all possible notification types
    NOTIFICATION_TYPE = (
        ("NEWPLACE", "newplace"),
        ("KIDUPDATE", "menuupdate"),
        ("FOLLOWED", "followed"),
        ("LIKED", "liked"),
        ("LIKEDPLACE", "likedplace"),
        ("COMMENTED", "commented")
    )
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE, default="GENERAL")
    # Indicates whether the notification was viewed or not.
    viewed = models.BooleanField(default=False)
    # The user that receiver the notification
    place = models.ForeignKey(to=Place, on_delete=models.CASCADE, blank=True, null=True)
    profile = models.ForeignKey(to=Profile, on_delete=models.CASCADE, blank=True, null=True)
    # A user that triggered the notification. For example, a follower, liker or a commenter.
    actor_user = models.ForeignKey(to=ModifiedUser, on_delete=models.CASCADE, blank=True, null=True)
