from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer, ProfileSerializer

# Create your views here.
@api_view(['POST'])
def signup(request):
    if request.data.get('password') != request.data.get('password2'):
        return Response({ 'error': '비밀번호 확인해주세요.' }, status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

@api_view(['GET'])
def profile(request, user_pk):    
    User = get_user_model()
    person = get_object_or_404(User, pk=user_pk) #1. username 일치하는 person 가져온다.
    serializer = ProfileSerializer(person) #2. 변환한다
    return Response(serializer.data) #3.응답한다

@api_view(['POST'])
def follow(request, user_pk):
    User = get_user_model()
    you = get_object_or_404(User, pk=user_pk)
    if request.user.is_authenticated:
        me = request.user
        if you != me:
            if you.followers.filter(pk=me.pk).exists():
                you.followers.remove(me)
                is_follow=False
            else:
                you.followers.add(me)
                is_follow=True
            data = {
                'is_follow' : is_follow,
                'cnt_followers':you.followers.count(),
                'cnt_followings':you.followings.count()
            }
            return JsonResponse(data)
        return HttpResponse(status=200)
    return Response(status=status.HTTP_403_FORBIDDEN)

# def playlist(request, username):
#     pass


# def login(reqeust):
#     pass

# def logout(request):
#     pass

