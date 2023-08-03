from typing import OrderedDict
from django.http import Http404, JsonResponse
from rest_framework.generics import get_object_or_404, CreateAPIView, ListAPIView, DestroyAPIView
from accounts.models import ModifiedUser
from profiles.models import Comment, Profile
from profiles.permissions import IsProfileOwner
from profiles.serializers import CommentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


class FetchComments(ListAPIView):
    """Fetch comments from a specific profile"""
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Comment.objects.filter(profile_id=self.kwargs['profile_id'])

    def dispatch(self, request, *args, **kwargs):
        if not Profile.objects.filter(id=self.kwargs['profile_id']):
            return JsonResponse({"detail": "Profile ID for Comments is not found"}, status=404)
        return super().dispatch(request, *args, **kwargs)


class CreateComments(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Must be authenticated

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(
                Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(profile=self.profile, user=ModifiedUser.objects.get(id=self.request.user.id))


class DeleteComment(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = get_object_or_404(
                Profile, id=self.kwargs['profile_id'])
        except Http404:
            return JsonResponse({"detail": "Profile not found"}, status=404)

        try:
            get_object_or_404(Comment, id=self.kwargs['pk'])
        except Http404:
            return JsonResponse({"detail": "Comment not found"}, status=404)

        return super().dispatch(request, *args, **kwargs)
