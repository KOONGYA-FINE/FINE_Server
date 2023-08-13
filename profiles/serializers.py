from rest_framework import serializers
from accounts.models import User
from config.settings import AWS_S3_CUSTOM_DOMAIN, AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
import boto3

VALID_IMAGE_EXTENSIONS = [ "jpg", "jpeg", "png", "gif", ]
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)
    sns = serializers.CharField(required=False)
    
    def put_data(self, userName, data):  
        saved = User.objects.get(username=userName)
        username = data.get('username', None)
        if username is None:
            username = saved.username
        elif User.objects.filter(username=username) and username is not saved.username:
            raise serializers.ValidationError("username already exists")
        
        image = data.get('image', None)
        sns = data.get('sns', None)

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
            image = saved.profile_image

        if sns is None:
            sns = saved.sns_link

        data = {
            "username" : username,
            "image" : image,
            "sns" : sns
        }
        user = User.objects.put_data(saved.id, data) 
        return self.get_data(user)

    def get_data(self, user):
        data = {
            "username" : user.username,
            "nation" : {
                "en" : user.nation.name,
                "kr" : user.nation.name_KR
            } ,
            "birth" : user.birth,
            "school" : user.school,
            "gender" : user.gender,
            "image" : str(user.profile_image),
            "sns" : user.sns_link,
            "date_joined" : user.date_joined,
        }
        return data
    
    class Meta:
        model = User
        exclude = ['email', 'password', 'token', 'last_login', 'gender', 'school', 'nation']