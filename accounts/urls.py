from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name='accounts'
urlpatterns=[
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', views.signup, name='signup'),
    # path('login/', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),
    path('<str:user_pk>/', views.profile, name='profile'),
    path('<int:user_pk>/follow/', views.follow, name='follow'),
    # path('<str:username>/playlist/', views.playlist, name='playlist'),
]