from django.db import models
from accounts.models import User
from config.settings import AWS_S3_CUSTOM_DOMAIN


class Place(models.Model):
    place_id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="맛집 이름", max_length=100)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(verbose_name="평점", default=0)  # 평점 - 리뷰 평점 평균
    address = models.CharField(verbose_name="주소명", max_length=300, default="")
    latitude = models.CharField(verbose_name="위도", max_length=20)
    longitude = models.CharField(verbose_name="경도", max_length=20)
    tag = models.CharField(verbose_name="태그", max_length=100)
    image = models.ImageField(
        verbose_name="맛집 이미지",
        blank=True,
        upload_to="",
        default=f"https://{AWS_S3_CUSTOM_DOMAIN}/FINE_LOGO.png",
    )  # S3
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
