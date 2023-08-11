from django.urls import path
from profiles.views import *

urlpatterns = [
    path("<int:userId>/posts/", GetPosts.as_view()),
    path("<int:userId>/saved/posts/", GetSavedPosts.as_view()),

    path('<int:userId>/', UserProfile.as_view()),
]
