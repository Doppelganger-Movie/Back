from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Review
from movies.models import Movie
from .serializers import ReviewSerializer


@api_view(['GET','POST'])#이게 없으면 AssertionError(accepted_renderer) 에러 남.
def review_list_create(request, movie_pk):
    movie_instance = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'GET':
        reviews = get_list_or_404(Review, movie=movie_pk)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        #댓글 저장 로직
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(movie=movie_instance, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        #유효성 검사에 실패한 경우
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET', 'DELETE', 'PUT'])
def review_detail(request, movie_pk, review_pk):
    movie_instance = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, movie=movie_instance, pk=review_pk)
    
    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data) 

    elif request.method == 'DELETE':
        if request.user == review.user :
            review.delete()
            data = {
                'message': f'{review_pk}번 리뷰가 삭제되었습니다.',
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':
        if request.user == review.user :
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)