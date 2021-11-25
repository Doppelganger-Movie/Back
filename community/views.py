from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from django.shortcuts import render, get_list_or_404, get_object_or_404
from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleSerializer, CommentSerializer

@api_view(['GET', 'POST'])
def article_list_create(request):
    if request.method == 'GET':
        articles = get_list_or_404(Article) #1. 가져온다
        serializer = ArticleListSerializer(articles, many=True) #2.변환한다
        return Response(serializer.data) #3. 응답한다.
    
    elif request.method == 'POST':
        # print(request.user)
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PUT'])
def article_detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    
    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if request.user == article.user:
            article.delete()
            data = {
                'delete': f'데이터 {article_pk}번이 삭제되었습니다.'
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    #데이터 수정도 여기서 하면 적당!
    elif request.method == 'PUT':
        if request.user == article.user:
            serializer = ArticleSerializer(article, data=request.data)
            if serializer.is_valid(raise_exception=request.data):
                serializer.save()
                return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET','POST'])#이게 없으면 AssertionError(accepted_renderer) 에러 남.
def comment_list_create(request, article_pk):
    article_instance = get_object_or_404(Article, pk=article_pk)
    if request.method == 'GET':
        comments = get_list_or_404(Comment, article=article_pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        #댓글 저장 로직
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(article=article_instance, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        #유효성 검사에 실패한 경우
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET', 'DELETE', 'PUT'])
def comment_detail(request, article_pk, comment_pk):
    article_instance = get_object_or_404(Article, pk=article_pk)
    comment = get_object_or_404(Comment, article=article_instance, pk=comment_pk)
    
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data) 

    elif request.method == 'DELETE':
        if request.user == comment.user :
            comment.delete()
            data = {
                'message': f'댓글 {comment_pk}번이 삭제되었습니다.',
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':
        if request.user == comment.user :
            serializer = CommentSerializer(comment, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)



