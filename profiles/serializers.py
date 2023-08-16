from rest_framework import serializers
from accounts.models import User
from config.settings import AWS_S3_CUSTOM_DOMAIN, AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
import boto3

VALID_IMAGE_EXTENSIONS = [ "jpg", "jpeg", "png", "gif", ]
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    profile_image = serializers.ImageField(required=False)
    sns = serializers.CharField(required=False)
    school = serializers.CharField(read_only=True)
    gender = serializers.CharField(read_only=True)

    def get_data(self, user):
        data = {
            "username" : user.username,
            "birth" : user.birth,
            "school" : user.school,
            "gender" : user.gender,
            "nation" : user.nation.name,
            "nation_KR" : user.nation.name_KR,
            "image" : str(user.profile_image),
            "sns" : user.sns_link,
            "date_joined" : user.date_joined,
        }
        return data
    
    def update(self, profile, data):
        image = data.get('profile_image', None)
        if image is not None:
            if not image.name.split('.')[-1].lower() in VALID_IMAGE_EXTENSIONS:
                serializers.ValidationError("Not an Image File")
            s3 = boto3.client('s3',
                aws_access_key_id = AWS_ACCESS_KEY_ID,
                aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
                region_name = AWS_REGION)
            try:
                s3.upload_fileobj(image, AWS_STORAGE_BUCKET_NAME, image.name)
                img_url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{image.name}"
                data['profile_image'] = img_url
            except:
                raise serializers.ValidationError("InValid Image File")
        else:
            data._mutable = True        # profile_image 없으면
            data['profile_image'] = profile.profile_image
            data._mutable = False

        sns = data.get('sns', None)
        if sns is None or sns == '':
            data._mutable = True
            data['sns'] = profile.sns_link
            data._mutable = False

        username = data.get('username', None)
        print(type(username))
        print(username)
        if username is None or username == '':
            data._mutable = True
            data['username'] = profile.username
            data._mutable = False

        user = User.objects.put_data(profile.id, data)
        return self.get_data(user)

        
    class Meta:
        model = User
        exclude = ['email', 'password', 'token', 'last_login', 'is_superuser', 'is_admin', 'is_staff', 'is_active', 'is_allowed', 'groups', 'user_permissions']