from django.urls import path
from profiles.views import *

urlpatterns = [
    path("<int:userid>/posts/", GetPosts.as_view()),
    path("<int:userid>/saved/posts/", GetSavedPosts.as_view()),
]
