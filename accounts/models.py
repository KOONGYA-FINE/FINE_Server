from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, nation=None):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, password=password)
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, nation=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def put_token(self, email, token):
        user = User.objects.filter(email=email).update(token=token)         # save() 대신 update()
        return user
    
    def activate(self, email):
        user = User.objects.filter(email=email).update(is_allowed = True)
        return user

    def put_info(self, email, username, nation, birth, school, gender):
        user = User.objects.filter(email=email).update(
            username = username,
            nation = nation,
            birth = birth,
            school = school,
            gender = gender
            )
        return user


class Nation(models.Model):
    nation_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    name_KR = models.CharField(max_length=100)
    image = models.ImageField(upload_to="")


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()  # UserManager 사용

    email = models.EmailField(verbose_name="이메일", unique=True)
    username = models.CharField(verbose_name="이름", max_length=50, unique=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, blank=True, null=True)
    birth = models.DateField(verbose_name="생년월일", null=True)
    school = models.CharField(verbose_name="학교", max_length=100)
    profile_image = models.ImageField(verbose_name="프로필 이미지", null=True, upload_to="")  # S3
    sns_link = models.CharField(verbose_name="sns 계정", max_length=100, null=True)
    gender = models.CharField(verbose_name="성별", max_length=1)
    token = models.CharField(max_length=300)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_allowed = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=True)

    # User 커스터마이징할 때 User 식별용
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
