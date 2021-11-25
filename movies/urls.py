from  django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('topten_movie/', views.getToptenMovie, name='getToptenMovie'),
    path('<int:movie_pk>/', views.detail, name='detail'),
    path('director_movie/', views.director_movie, name='director_movie'),
]