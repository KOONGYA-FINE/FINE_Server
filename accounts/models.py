from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password, nation=None):
        if not email:
            raise ValueError("The Email field must be set")
        if not password:
            raise ValueError("The Password field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, nation=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(email=email, username=username, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class Nation(models.Model):
    nation_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=100)


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()  # UserManager 사용

    email = models.EmailField(verbose_name="이메일", unique=True)
    username = models.CharField(verbose_name="이름", max_length=50, unique=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, blank=True, null=True)
    birth = models.DateField(verbose_name="생년월일", null=True)
    school = models.CharField(verbose_name="학교", max_length=50)
    profile_image = models.CharField(verbose_name="프로필 이미지", max_length=30)
    sns_link = models.CharField(verbose_name="sns 계정", max_length=100)
    location = models.CharField(verbose_name="출신지", max_length=100)
    token = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    # User 커스터마이징할 때 User 식별용
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
