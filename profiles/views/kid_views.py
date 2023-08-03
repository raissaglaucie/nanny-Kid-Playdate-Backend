from typing import OrderedDict
from django.http import Http404, JsonResponse
from rest_framework.generics import get_object_or_404, CreateAPIView, UpdateAPIView, ListAPIView, \
    DestroyAPIView
from profiles.permissions import IsProfileOwner
from profiles.models import Kid, Profile
from profiles.serializers import KidSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponseRedirect
from django.urls import reverse


# ==================== Kid Views ========================
class CreateKid(CreateAPIView):
    serializer_class = KidSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(
                Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(profile=self.profile)


class UpdateKid(UpdateAPIView):
    queryset = Kid.objects.all()
    serializer_class = KidSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]
    http_method_names = ["patch"]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(
                Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        try:
            get_object_or_404(Kid, id=self.kwargs['pk'])
        except Http404:
            return JsonResponse({"detail": "Kid not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)


class FetchKids(ListAPIView):
    """
    Feth all kids corresponded to a specific profile_id
    """
    queryset = Kid.objects.all()
    serializer_class = KidSerializer
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        if not Profile.objects.filter(id=self.kwargs['profile_id']):
            return JsonResponse({"detail": "Profile not found"}, status=404)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Kid.objects.filter(profile_id=self.kwargs['profile_id'])


class DeleteKid(DestroyAPIView):
    queryset = Kid.objects.all()
    serializer_class = KidSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(
                Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        try:
            get_object_or_404(Kid, id=self.kwargs['pk'])
        except Http404:
            return JsonResponse({"detail": "Kid not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if response.status_code not in [401, 403, 404]:
            return HttpResponseRedirect(reverse('profiles:kids', kwargs={'profile_id': self.profile.id}))
        return response
