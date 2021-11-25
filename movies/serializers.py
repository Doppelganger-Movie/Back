from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Movie, Genre, Provider, Actor, Director
# from ..accounts.models import User

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        # fields = ['name']
        fields = '__all__'
        
class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'
        
class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = '__all__'
        
class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(read_only=True, many=True)
    directors = DirectorSerializer(read_only=True, many=True)
    actors = ActorSerializer(read_only=True, many=True)
    class Meta:
        model = Movie
        fields = '__all__'