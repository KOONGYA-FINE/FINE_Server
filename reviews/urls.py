from django.urls import path
from reviews.views import *

urlpatterns = [
    path("", ReviewList.as_view()),
    path("<int:reviewId>/", ReviewDetail.as_view()),
]
