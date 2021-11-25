from django.db import models
from django.conf import settings


class Genre(models.Model):
    name = models.CharField(max_length=50)
    

class Provider(models.Model):
    flatrate = models.TextField()
    buy = models.TextField()
    rent = models.TextField()


class Actor(models.Model):
    name = models.CharField(max_length=50)
    profile_path = models.CharField(max_length=200, blank=True)
    

class Director(models.Model):
    name = models.CharField(max_length=50)
    profile_path = models.CharField(max_length=200, blank=True)
    
    
class Movie(models.Model):
    adult = models.BooleanField()
    genres = models.ManyToManyField(Genre, related_name='genre_movie', blank=True)
    original_language = models.CharField(max_length=100)
    original_title = models.CharField(max_length=100)
    overview = models.TextField()
    poster_path = models.CharField(max_length=200, blank=True)
    release_date = models.CharField(max_length=50)
    runtime = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
    actors = models.ManyToManyField(Actor, related_name='actor_movie', blank=True)
    directors = models.ManyToManyField(Director, related_name='director_movie', blank=True)
    