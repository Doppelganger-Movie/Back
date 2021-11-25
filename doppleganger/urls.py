from django.urls import path
from . import views

app_name='doppleganger'
urlpatterns = [
    path('images/', views.analyze_image, name='analyze_image'),
    path('',views.doppleganger, name='doppleganger'),
    path('<int:user_id>/', views.get_doppleganger, name="get_doppleganger")
]