from django.urls import path
from . import views

app_name='reviews'
urlpatterns = [
    path('<int:movie_pk>/<int:review_pk>/', views.review_detail),
    path('<int:movie_pk>/', views.review_list_create),
]