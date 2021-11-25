from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SelfImage

class SelfImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfImage
        fields = '__all__'
        read_only_fields = ['upload_user', 'upload_image']