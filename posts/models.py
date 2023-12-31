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
    title = models.CharField(verbose_name="제목", max_length=100)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(verbose_name="내용", max_length=400)
    interest = models.CharField(
        verbose_name="관심사", max_length=100, default=None, null=True
    )  # 디폴트 값 추가
    is_deleted = models.BooleanField(default=False)  # 삭제 여부 확인


class Post_KR(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    title = models.CharField(verbose_name="한국어 제목", max_length=100)
    content = models.CharField(verbose_name="한국어 내용", max_length=400, default="")
    is_deleted = models.BooleanField(default=False)


class SavedPosts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_en = models.ForeignKey(Post, on_delete=models.CASCADE)
    post_kr = models.ForeignKey(Post_KR, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ["user", "post_en", "post_kr"]  # 중복 스크랩 방지
