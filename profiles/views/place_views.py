from typing import OrderedDict
from django.http import Http404, JsonResponse
from rest_framework.generics import get_object_or_404, CreateAPIView, UpdateAPIView, ListAPIView, \
    DestroyAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination

from accounts.models import ModifiedUser
from ..permissions import IsProfileOwner
from ..models import Place, Notification, Profile
from ..serializers import PlaceSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponseRedirect
from django.urls import reverse


class GetPlaces(RetrieveAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        if not Place.objects.filter(id=self.kwargs['place_id']):
            return JsonResponse({"detail": "Place ID is not found"}, status=404)
        self.place = get_object_or_404(Place, id=self.kwargs['place_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.place

    def retrieve(self, request, *args, **kwargs):
        ret = super().retrieve(request, *args, **kwargs)
        if 'id' not in ret.data:
            return JsonResponse({"detail": "Place ID is not found"}, status=404)
        return ret


class GetAllPlaces(ListAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]


class GetPlaceProfile(ListAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(
                Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        # Reference: https://stackoverflow.com/questions/44033670/python-django-rest-framework-unorderedobjectlistwarning
        return Place.objects.filter(profile=self.profile).order_by('id')


class DeletePlace(DestroyAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def dispatch(self, request, *args, **kwargs):
        if not Place.objects.filter(id=self.kwargs['pk']):
            return JsonResponse({"detail": "Place ID is not found"}, status=404)
        self.profile = get_object_or_404(
            Place, id=self.kwargs['pk']).profile
        return super().dispatch(request, *args, **kwargs)

    # Redirect to my profile after remove a place?
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if response.status_code not in [401, 403, 404]:
            return HttpResponseRedirect(reverse('profiles:get-all-place'))
        return response


class CreatePlace(CreateAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated,
                          IsProfileOwner]  # Must be authenticated

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(
                Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(profile=self.profile, user=ModifiedUser.objects.get(id=self.request.user.id))


class LikePlace(UpdateAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def dispatch(self, request, *args, **kwargs):
        if not Place.objects.filter(id=self.kwargs['place_id']):
            return JsonResponse({"detail": "Place ID is not found"}, status=404)
        self.place = get_object_or_404(Place, id=self.kwargs['place_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        # Making this endpoint ignore the given body
        for field in serializer.fields:
            serializer.fields[field].read_only = True
        return serializer

    def update(self, request, *args, **kwargs):
        # Check if the current place is already followed by this user
        if self.place.likes.filter(id=self.request.user.id).exists():
            return JsonResponse({"detail": "User already liked this place"}, status=409)
        self.kwargs['pk'] = self.kwargs['place_id']
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.profile = self.place.profile
        current_user = ModifiedUser.objects.get(id=self.request.user.id)
        Notification.objects.create(type="LIKEDPLACE", user=self.profile.owner,
                                    profile=self.profile, actor_user=current_user)
        serializer.validated_data.update({'likes': [current_user]})
        return super().perform_update(serializer)


class UnlikePlace(UpdateAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def dispatch(self, request, *args, **kwargs):
        if not Place.objects.filter(id=self.kwargs['place_id']):
            return JsonResponse({"detail": "Place ID is not found"}, status=404)
        self.place = get_object_or_404(Place, id=self.kwargs['place_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        # Making this endpoint ignore the given body
        for field in serializer.fields:
            serializer.fields[field].read_only = True
        return serializer

    def update(self, request, *args, **kwargs):
        # Check if the current profile is followed by this user
        if not self.place.likes.filter(id=self.request.user.id).exists():
            return JsonResponse({"detail": "User does not like this place"}, status=409)
        self.kwargs['pk'] = self.kwargs['place_id']
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.place.likes.remove(
            ModifiedUser.objects.get(id=self.request.user.id))
        return super().perform_update(serializer)


class FetchIfLikedPlace(RetrieveAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        if not Place.objects.filter(id=self.kwargs['place_id']):
            return JsonResponse({"detail": "Place ID is not found"}, status=404)
        self.place = get_object_or_404(Place, id=self.kwargs['place_id'])
        return super().dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code not in [401, 403, 404]:
            response.data = {'is_liked': self.place.likes.filter(
                id=self.request.user.id).exists()}
        return super().finalize_response(request, response, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.kwargs['place_id']
        place = super().retrieve(request, *args, **kwargs)
        if 'id' not in place.data:
            return JsonResponse({"detail": "Place with the given name was not found"}, status=404)
        return place
    


class GetPlaceFeed(ListAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        curr_user = ModifiedUser.objects.get(id=self.request.user.id)
        try:
            followed_prof = Profile.objects.filter(followers=curr_user)
        except Profile.DoesNotExist:
            followed_prof = None
        print(followed_prof)
        # return Blog.objects.filter(likes=curr_user) # Method to get all liked blogs
        return Place.objects.filter(profile__in=followed_prof).order_by('id')
