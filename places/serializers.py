from rest_framework import serializers
from .models import Place
import boto3
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN

VALID_IMAGE_EXTENSIONS = [ "jpg", "jpeg", "png", "gif", ]

class PlaceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only = True)
    name = serializers.CharField(required=True)
    username = serializers.CharField(source="user.username", read_only = True)
    user_image = serializers.ImageField(source="user.profile_image", read_only = True)
    score = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
    tag = serializers.CharField(required=True)
    content = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)  # S3

    def validate(self, data): 
        image = data.get('image')
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
                data['image'] = img_url
                return data
            except:
                raise serializers.ValidationError("Invalid Image File")
        return data
    class Meta:
        model = Place
        fields = "__all__"
