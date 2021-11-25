from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from rest_framework.serializers import Serializer
from .models import Director, Movie
# from ..reviews.models import Review
from rest_framework.response import Response
from .serializers import DirectorSerializer, MovieSerializer, GenreSerializer
from reviews.serializers import ReviewSerializer
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET'])
def getToptenMovie(reqeust):
    movie_list = Movie.objects.order_by('-vote_count')[:10]
    serializer = MovieSerializer(movie_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def detail(reqeust, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    # print(movie)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def director_movie(request):
    User = get_user_model()
    person = get_object_or_404(User, username=request.user)
    person_review = person.reviews.all()
    serializer_review = ReviewSerializer(person_review, many=True)  # user가 쓴 리뷰들을 다 불러옴
    movie_list = [[],[],[],[],[]]
    # user가 쓴 리뷰 중에서 제일 평점이 높은 것들 movie_list에 movie_id 저장함.
    for i in range(len(serializer_review.data)):
        idx = int(serializer_review.data[i]['vote']) - 1
        if serializer_review.data[i]['vote'] == 5.0 :
            movie_list[4].append(serializer_review.data[i]['movie'])
        elif len(movie_list[4]):
            continue
        else:
            movie_list[idx].append(serializer_review.data[i]['movie'])
    # 평점 리스트들 중 가장 높은 평점 가지고 있는 영화 리스트들을 가지고옴.
    if len(movie_list[4]):
        movie_list_final = movie_list[4]
    elif len(movie_list[3]):
        movie_list_final = movie_list[3]
    elif len(movie_list[2]):
        movie_list_final = movie_list[2]
    elif len(movie_list[1]):
        movie_list_final = movie_list[1]
    else:
        movie_list_final = movie_list[0]
    director_list = {}
    for movie_id in movie_list_final:
        movie = get_object_or_404(Movie, pk=movie_id)
        serializer_movie = MovieSerializer(movie)
        director_id = serializer_movie.data['directors'][0]['id']
        if director_id in director_list:
            director_list[director_id] = director_list[director_id] + 1
        else:
            director_list[director_id] = 1
    # 제일 많이 언급된 감독의 정보를 받아옴.
    director_list_sort = sorted(director_list.items(), key=lambda x: -x[1])
    director_id=director_list_sort[0][0]
    director = get_object_or_404(Director, pk=director_id)
    # 그 감독의 movie를 넘겨줌.
    movies = director.director_movie.all()
    serializer_movie = MovieSerializer(movies, many=True)

    return Response(serializer_movie.data)

