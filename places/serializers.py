from rest_framework import serializers
from .models import Place
from accounts.models import User
import boto3
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN

VALID_IMAGE_EXTENSIONS = [ "jpg", "jpeg", "png", "gif", ]

class PlaceSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only = True)
    user_image = serializers.CharField(source="user.profile_image", read_only = True)
    image = serializers.CharField(read_only = True)  # S3

    class Meta:
        model = Place
        fields = "__all__"

class PlaceImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only = True)
    name = serializers.CharField(required=True)
    user = serializers.IntegerField(source="user.id", read_only = True)
    username = serializers.CharField(source="user.username", read_only = True)
    user_image = serializers.CharField(source="user.profile_image", read_only = True)
    score = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
    tag = serializers.CharField(required=True)
    content = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)  # S3
    
    def get_data(self, place):
        data = {
            'id' : place.id,
            'name' : place.name,
            'user_id' : place.user.id,
            'username' : place.user.username,
            'user_image' : str(place.user.profile_image),
            'score' : place.score,
            'address' : place.address,
            'latitude' : place.latitude,
            'longitude' : place.longitude,
            'tag' : place.tag,
            'content' : place.content,
            'image' : str(place.image),
        }
        return data

    def create(self, data):
        image = data.get('image')

        if image is not None and type(image) is not str:
            if not image.name.split('.')[-1].lower() in VALID_IMAGE_EXTENSIONS:
                serializers.ValidationError("Not an Image File")
            s3 = boto3.client('s3',
                aws_access_key_id = AWS_ACCESS_KEY_ID,
                aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
                region_name = AWS_REGION)
            try:
                s3.upload_fileobj(image, AWS_STORAGE_BUCKET_NAME, image.name)
                img_url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{image.name}"
                data._mutable = True
                data['image'] = img_url
                data._mutable = False
            except Exception as e:
                print(f"Error uploading image: {e}")
                raise serializers.ValidationError("Invalid Image File")
        else:
            data._mutable = True        # image 없으면
            data['image'] = f'https://{AWS_S3_CUSTOM_DOMAIN}/FINE_LOGO.png'
            data._mutable = False
        place = Place.objects.create(name=data.get('name'), user=User.objects.get(id=data.get('user')), score=data.get('score'), address=data.get('address'), 
                                     latitude=data.get('latitude'), longitude=data.get('longitude'), tag=data.get('tag'), content=data.get('content', None), image=data.get('image'))
        return self.get_data(place)


    def update(self, place, data):
        
        score = data.get('score', None)
        if score is None:
            score = place.score
        tag = data.get("tag", None)
        if tag is None:
            tag = place.tag
        content = data.get('content', None)
        if content is None:
            content = place.content

        image = data.get('image', None)
        if image is not None and type(image) is not str:
            if not image.name.split('.')[-1].lower() in VALID_IMAGE_EXTENSIONS:
                serializers.ValidationError("Not an Image File")
            s3 = boto3.client('s3',
                aws_access_key_id = AWS_ACCESS_KEY_ID,
                aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
                region_name = AWS_REGION)
            try:
                s3.upload_fileobj(image, AWS_STORAGE_BUCKET_NAME, image.name)
                img_url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{image.name}"
                image = img_url
            except:
                image = place.image
        else:
            image = place.image

        place.score = score
        place.tag = tag
        place.content = content
        place.image = image
        place.save()

        return self.get_data(place)

    
    class Meta:
        model = Place
        fields = "__all__"
