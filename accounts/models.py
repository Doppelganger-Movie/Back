from django.db import models
from django.contrib.auth.models import AbstractUser
from movies.models import Movie, Actor 

# Create your models here.
class User(AbstractUser):
    bookmark = models.ManyToManyField(Movie, related_name='user', blank=True)
    doppleganger = models.ManyToManyField(Actor, related_name='user', blank=True)
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

