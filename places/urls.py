from django.urls import path
from places.views import *


urlpatterns = [
    path("", PlaceList.as_view()),
    path("<int:id>/", PlaceDetail.as_view()),
]
