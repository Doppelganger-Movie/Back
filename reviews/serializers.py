from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_list_or_404, get_object_or_404

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    class Meta:
        model = Review
        # fields = ['id', 'user_id', 'movie_id', 'content', 'voted',  'created_at', 'updated_at']
        fields = '__all__'
        read_only_fields = ['user', 'movie']

    def get_username(self, obj):
        user = get_object_or_404(get_user_model(),username=obj.user)
        return user.username