from django.db import models
from accounts.models import User
from places.models import Place


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name="작성일시", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="수정일시", auto_now=True)

    class Meta:
        abstract = True


class Review(BaseModel):
    review_id = models.AutoField(primary_key=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    content = models.CharField(verbose_name="리뷰", max_length=200)
    review_image = models.ImageField(verbose_name="리뷰 이미지", null=True)  # S3


class Review_KR(BaseModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    content = models.CharField(verbose_name="한국어 내용", max_length=200)
