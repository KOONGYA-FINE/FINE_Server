from django.urls import path
from profiles.views import *

urlpatterns = [
    path("<str:userName>/posts/", GetPosts.as_view()),
    path("<str:userName>/saved/posts/", GetSavedPosts.as_view()),
    path("<str:userName>/places/", GetPlaces.as_view()),
    path("<str:userName>/reviews/", GetReviews.as_view()),
    path("<str:userName>/", UserProfile.as_view()),
]
