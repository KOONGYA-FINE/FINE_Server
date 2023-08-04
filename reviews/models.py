from django.db import models
from accounts.models import User
from places.models import Place


# Create your models here.
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    content = models.CharField(verbose_name="리뷰", max_length=100)
    image = models.ImageField(verbose_name="리뷰 이미지", null=True)  # S3
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)