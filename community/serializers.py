from django.contrib.auth import get_user_model
from django.shortcuts import render, get_list_or_404, get_object_or_404
from rest_framework import serializers
from .models import Article, Comment

class ArticleListSerializer(serializers.ModelSerializer):    
    username = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = ('username', 'user', 'id', 'title', 'content', 'created_at', 'updated_at')
        read_only_fields = ['user']

    def get_username(self, obj):
        user = get_object_or_404(get_user_model(),username=obj.user)
        return user.username

class ArticleSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['user']

    def get_username(self, obj):
        user = get_object_or_404(get_user_model(),username=obj.user)
        return user.username



class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields='__all__'
        read_only_fields = ['article', 'user'] #사용자로부터 입력받는 값이 아니다.
    def get_username(self, obj):
        user = get_object_or_404(get_user_model(),username=obj.user)
        return user.username