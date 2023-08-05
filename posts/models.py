from django.db import models
from accounts.models import User

# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name="작성일시", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="수정일시", auto_now=True)

    class Meta:
        abstract = True


class Post(BaseModel):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="제목", max_length=50)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(verbose_name="내용", max_length=200)
    image = models.ImageField(verbose_name="이미지", null=True)  # S3
    interest = models.CharField(verbose_name="관심사", max_length=100)


class Post_KR(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="한국어 제목", max_length=50)
    content = models.CharField(verbose_name="한국어 내용", max_length=200)
