from django.db import models
from accounts.models import Nation, User


class Place(models.Model):
    place_id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="맛집 이름", max_length=100)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(verbose_name="평점", default=0)  # 평점
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
    latitude = models.CharField(verbose_name="위도", max_length=20)
    longitude = models.CharField(verbose_name="경도", max_length=20)
    tag = models.CharField(verbose_name="태그", max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)