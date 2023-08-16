from django.db import models
from accounts.models import User
from config.settings import AWS_S3_CUSTOM_DOMAIN


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="맛집 이름", max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(verbose_name="평점", default=0)
    address = models.CharField(verbose_name="주소명", max_length=300, default="")
    latitude = models.FloatField(verbose_name="위도", max_length=20)
    longitude = models.FloatField(verbose_name="경도", max_length=20)
    tag = models.CharField(verbose_name="태그", max_length=100)
    content = models.CharField(verbose_name="리뷰", max_length=200)
    image = models.CharField(default="https://{AWS_S3_CUSTOM_DOMAIN}/FINE_LOGO.png", max_length=100)  # S3
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)