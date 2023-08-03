from typing import OrderedDict
from django.http import Http404, JsonResponse
from rest_framework.generics import get_object_or_404, CreateAPIView, UpdateAPIView, ListAPIView, \
    DestroyAPIView, RetrieveAPIView
from accounts.models import ModifiedUser
from profiles.permissions import IsProfileOwner
from profiles.models import  Kid, Notification, Profile
from profiles.serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponseRedirect
from django.urls import reverse

class CreateProfile(CreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        self.owner = ModifiedUser.objects.get(id=request.user.id)
        if Profile.objects.filter(owner=self.owner):
            return JsonResponse({"detail": "Same user cannot own more than one profile"}, status=409)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(owner=self.owner)


class FetchAllProfiles(ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]


class FetchProfileById(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.profile

    def retrieve(self, request, *args, **kwargs):
        ret = super().retrieve(request, *args, **kwargs)
        if 'id' not in ret.data:
            return JsonResponse({"detail": "Profile was not found"}, status=404)
        return ret


class FetchMyProfile(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        try:
            self.profile = Profile.objects.get(owner=ModifiedUser.objects.get(id=self.request.user.id))
        except Profile.DoesNotExist:
            self.profile = None
        return self.profile

    def retrieve(self, request, *args, **kwargs):
        ret = super().retrieve(request, *args, **kwargs)
        if 'id' not in ret.data:
            return JsonResponse({"detail": "Profile was not found"}, status=404)
        return ret


class FetchIfFollowsProfile(RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)
        return super().dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code not in [401, 403, 404]:
            response.data = {'is_followed': self.profile.followers.filter(id=self.request.user.id).exists()}
        return super().finalize_response(request, response, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.kwargs['profile_id']
        ret = super().retrieve(request, *args, **kwargs)
        if 'id' not in ret.data:
            return JsonResponse({"detail": "Profile with the given name was not found"}, status=404)
        return ret

class FetchIfLikedProfile(RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "profile not found"}, status=404)
        return super().dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code not in [401, 403, 404]:
            response.data = {'is_liked': self.profile.likes.filter(id=self.request.user.id).exists()}
        return super().finalize_response(request, response, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.kwargs['profile_id']
        ret = super().retrieve(request, *args, **kwargs)
        if 'id' not in ret.data:
            return JsonResponse({"detail": "profile with the given name was not found"}, status=404)
        return ret

class FetchFollowersProfiles(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "profile not found"}, status=404)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.profile

    def retrieve(self, request, *args, **kwargs):
        ret = super().retrieve(request, *args, **kwargs)
        if 'id' not in ret.data:
            return JsonResponse({"detail": "profile with the given id was not found"}, status=404)
        ret.data = OrderedDict({'followers': ret.data['followers']})
        return ret


class UpdateProfileInfo(UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]
    http_method_names = ["patch"]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.kwargs['profile_id']
        return super().update(request, *args, **kwargs)


class FollowProfile(UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        # Making this endpoint ignore the given body
        for field in serializer.fields:
            serializer.fields[field].read_only = True
        return serializer

    def update(self, request, *args, **kwargs):
        # Check if the current profile is already followed by this user
        if self.profile.followers.filter(id=self.request.user.id).exists():
            return JsonResponse({"detail": "User already follows this profile"}, status=409)
        self.kwargs['pk'] = self.kwargs['profile_id']
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        current_user = ModifiedUser.objects.get(id=self.request.user.id)
        Notification.objects.create(type="FOLLOWED", user=self.profile.owner,
                                    profile=self.profile, actor_user=current_user)
        serializer.validated_data.update({'followers': [current_user]})
        return super().perform_update(serializer)


class UnfollowProfile(UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        # Making this endpoint ignore the given body
        for field in serializer.fields:
            serializer.fields[field].read_only = True
        return serializer

    def update(self, request, *args, **kwargs):
        # Check if the current profile is followed by this user
        if not self.profile.followers.filter(id=self.request.user.id).exists():
            return JsonResponse({"detail": "User does not follow this profile"}, status=409)
        self.kwargs['pk'] = self.kwargs['profile_id']
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.profile.followers.remove(ModifiedUser.objects.get(id=self.request.user.id))
        return super().perform_update(serializer)


class LikeProfile(UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        # Making this endpoint ignore the given body
        for field in serializer.fields:
            serializer.fields[field].read_only = True
        return serializer

    def update(self, request, *args, **kwargs):
        # Check if the current profile is already followed by this user
        if self.profile.likes.filter(id=self.request.user.id).exists():
            return JsonResponse({"detail": "User already likes this profile"}, status=409)
        self.kwargs['pk'] = self.kwargs['profile_id']
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        current_user = ModifiedUser.objects.get(id=self.request.user.id)
        Notification.objects.create(type="LIKED", user=self.profile.owner,
                                    profile=self.profile, actor_user=current_user)
        serializer.validated_data.update({'likes': [current_user]})
        return super().perform_update(serializer)


class UnlikeProfile(UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        # Making this endpoint ignore the given body
        for field in serializer.fields:
            serializer.fields[field].read_only = True
        return serializer

    def update(self, request, *args, **kwargs):
        # Check if the current profile is followed by this user
        if not self.profile.likes.filter(id=self.request.user.id).exists():
            return JsonResponse({"detail": "User does not like this profile"}, status=409)
        self.kwargs['pk'] = self.kwargs['profile_id']
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.profile.likes.remove(ModifiedUser.objects.get(id=self.request.user.id))
        return super().perform_update(serializer)


class FetchProfileByArg(ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Profile.objects.all()
        profile_name = self.request.GET.get('name', None)
        profile_postal_code = self.request.GET.get('postal_code', None)
        if profile_name:
            # Reference: https://stackoverflow.com/questions/45190151/there-is-a-way-to-check-if-a-model-field-contains-a-substring
            if profile_postal_code:
                queryset = queryset.filter(name__icontains=profile_name, postal_code=profile_postal_code).order_by('id')
            else:
                queryset = queryset.filter(name__icontains=profile_name).order_by('id')

        elif profile_postal_code:
            queryset = queryset.filter(postal_code=profile_postal_code).order_by('id')
        return queryset

