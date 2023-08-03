from django.urls import path

from .views.place_views import *
from .views.kid_views import *
from .views.comment_views import *
from .views.profile_views import *

app_name = 'profiles'


urlpatterns = [
    # Kid endpoints
    path('<int:profile_id>/kids/new/', CreateKid.as_view(), name='create-kid'),
    path('<int:profile_id>/kids/<int:pk>/edit/', UpdateKid.as_view(), name='update-kid'),
    path('<int:profile_id>/kids/items/', FetchKids.as_view(), name='kids'),
    path('<int:profile_id>/kids/<int:pk>/remove/', DeleteKid.as_view(), name='delete-kid'),
    
                
    # Profile endpoints
    path('new/', CreateProfile.as_view(), name='profile-create'),
    path('all/', FetchAllProfiles.as_view(), name='profiles'),
    path('owned/', FetchMyProfile.as_view(), name='get-owned-profile'),
    path('doesfollow/<int:profile_id>/',
         FetchIfFollowsProfile.as_view(), name='profile-doesfollow'),
    path('doeslike/<int:profile_id>/',
         FetchIfLikedProfile.as_view(), name='profile-doeslike'),
    path('info/<int:profile_id>/',
         FetchProfileById.as_view(), name='profile-byid'),
    path('search/', FetchProfileByArg.as_view(), name='profile-byarg'),
    path('<int:profile_id>/followers/',
         FetchFollowersProfiles.as_view(), name='profile-followers'),
    path('<int:profile_id>/edit/',
         UpdateProfileInfo.as_view(), name='profile-edit'),
    path('<int:profile_id>/follow/',
         FollowProfile.as_view(), name='profile-follow'),
    path('<int:profile_id>/unfollow/',
         UnfollowProfile.as_view(), name='profile-unfollow'),
    path('<int:profile_id>/like/',
         LikeProfile.as_view(), name='profile-like'),
    path('<int:profile_id>/unlike/',
         UnlikeProfile.as_view(), name='profile-unlike'),


    # Comment endpoints
    path('<int:profile_id>/comments/all/',
         FetchComments.as_view(), name='fetch-comments'),
    path('<int:profile_id>/comments/new/',
         CreateComments.as_view(), name='create-comments'),
    path('<int:profile_id>/comments/<int:pk>/remove/',
         DeleteComment.as_view(), name='delete-comment'),

    # Place endpoints
    path('places/<int:place_id>/', GetPlaces.as_view(), name='get-place'),
    path('places/<int:pk>/delete/', DeletePlace.as_view(), name='delete-place'),
    path('<int:profile_id>/places/new/', CreatePlace.as_view(), name='create-place'),
    path('places/<int:place_id>/like/', LikePlace.as_view(), name='like-place'),
    path('places/<int:place_id>/unlike/', UnlikePlace.as_view(), name='unlike-place'),
    path('places/all/', GetAllPlaces.as_view(), name='get-all-place'),
    path('places/doeslike/<int:place_id>/', FetchIfLikedPlace.as_view(), name='doeslike-place'),
    path('places/feed/', GetPlaceFeed.as_view(), name='get-place-feed'), #DUAS ROTAS NOVAS
    path('<int:profile_id>/places/', GetPlaceProfile.as_view(), name='get-prof-blog'),
]