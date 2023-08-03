from rest_framework import serializers

from accounts.serializers import ModifiedUserSerializer
from profiles.models import Place, Notification, Comment, Kid, Profile


class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField()
    followers = serializers.ReadOnlyField()
    views = serializers.ReadOnlyField()
    likes = serializers.ReadOnlyField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        self.owner = rep.get("owner", None)
        if self.owner:
            rep.pop('owner')
            rep.update({'owner_id': self.owner.id})

            followers = []
            likes = []

            if "followers" in rep:
                for follower in rep["followers"].all().iterator():
                    followers.append(ModifiedUserSerializer(follower).data)

            if "likes" in rep:
                for like in rep["likes"].all().iterator():
                    likes.append(ModifiedUserSerializer(like).data)

            rep.update({"followers": followers, "likes": likes})
        return rep

    def update(self, instance, validated_data):
        if 'followers' in validated_data:
            # add a follower to the many-to-many field of followers
            followers = validated_data.pop('followers')
            for follower in followers:
                instance.followers.add(follower)

        if 'likes' in validated_data:
            # add a follower to the many-to-many field of followers
            likes = validated_data.pop('likes')
            for like in likes:
                instance.likes.add(like)
        return super().update(instance, validated_data)

    class Meta:
        model = Profile
        fields = ['id', 'owner', 'followers', 'name', 'address',
                  'email', 'phone_num', 'views', 'likes', 'profile_pic', 'postal_code']


class KidSerializer(serializers.ModelSerializer):
    profile = serializers.ReadOnlyField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not hasattr(self, "profile"):
            self.profile = rep.get("profile", None)
        rep.pop('profile')
        rep.update({'profile_id': self.profile.id})
        return rep

    def create(self, validated_data):
        self.profile = validated_data.get("profile", None)
        for follower in self.profile.followers.all().iterator():
            Notification.objects.create(type="KIDUPDATE", user=follower,
                                        profile=self.profile)
        return super().create(validated_data)

    class Meta:
        model = Kid
        fields = ['id', 'name', 'description',
                  'age', 'picture', 'profile']


# Comments Serializer
class CommentSerializer(serializers.ModelSerializer):
    profile = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField()
    timestamp = serializers.ReadOnlyField(required=False)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not hasattr(self, "profile"):
            self.profile = rep.get("profile", None)
        rep.pop('profile')
        if "user" in rep:
            rep.update({'user': ModifiedUserSerializer(rep["user"]).data})
        rep.update({'profile_id': self.profile.id})
        return rep

    def create(self, validated_data):
        self.profile = validated_data.get("profile", None)
        comment = Comment.objects.create(
            # user=ModifiedUserSerializer(validated_data['user']).data,
            user=validated_data['user'],
            contents=validated_data['contents'],
            # timestamp=timezone.now(),
            profile=validated_data['profile'],
        )
        Notification.objects.create(type="COMMENTED", user=self.profile.owner,
                                    actor_user=validated_data['user'],
                                    profile=validated_data['profile'])  # Owner gets the notification
        # return super().create(validated_data)
        return comment

    class Meta:
        model = Comment
        fields = ['id', 'user', 'timestamp', 'profile', 'contents']


class PlaceSerializer(serializers.ModelSerializer):
    profile = serializers.ReadOnlyField()
    publish_timestamp = serializers.ReadOnlyField(required=False)
    likes = serializers.ReadOnlyField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        self.profile = rep.get("profile", None)
        if self.profile:
            rep.pop('profile')
            rep.update({'profile_id': self.profile.id})

            likes = []

            if "likes" in rep:
                for like in rep["likes"].all().iterator():
                    likes.append(ModifiedUserSerializer(like).data)

            rep.update({"likes": likes})
        return rep

    def create(self, validated_data):
        self.profile = validated_data.get("profile", None)
        place = Place.objects.create(
            profile=validated_data['profile'],
            place_pic=validated_data['place_pic'] if 'place_pic' in validated_data else None,
            title=validated_data['title'],
            contents=validated_data['contents'],
        )
        # Creating a notification for all followers regarding the new blog
        for follower in self.profile.followers.all().iterator():
            Notification.objects.create(type="NEWPLACE", user=follower,
                                        profile=self.profile)  # Followers get the notification
        # return super().create(validated_data)
        return place

    def update(self, instance, validated_data):
        if 'likes' in validated_data:
            # add a follower to the many-to-many field of followers
            likes = validated_data.pop('likes')
            for like in likes:
                instance.likes.add(like)
        return super().update(instance, validated_data)

    class Meta:
        model = Place
        fields = ['id', 'profile', 'title', 'place_pic',
                  'contents', 'publish_timestamp', 'likes']
