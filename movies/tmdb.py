import requests
import json
from decouple import config

apiKey = config('TMDB_KEY')

base_url = 'https://api.themoviedb.org/3'    # TMDB API 이용
movies_id = []
actors_directors_data = []

# MOVIES - Get Popular 
def get_movie_popular_url(page='1'):
    request_url = base_url + f'/movie/popular?api_key={apiKey}&language=ko-KR&page={page}'
    return request_url


# MOVIES - Get Details
def get_details_url(movie_id):
    request_url = base_url + f'/movie/{movie_id}?api_key={apiKey}&language=ko-KR'
    return request_url
    

# GENRES - Get Movie List 
def get_genre_url():
    request_url = base_url + f'/genre/movie/list?api_key={apiKey}&language=ko-KR'
    return request_url

def get_watch_providers(movie_id):
    request_url = base_url + f'/movie/{movie_id}/watch/providers?api_key={apiKey}'
    return request_url

# 장르 목록 json으로 만들기
def create_genre_data():
    genre_data = []
    
    url = get_genre_url()
    raw_data = requests.get(url)
    json_data = raw_data.json()
    genres = json_data.get('genres')
        
    for genre in genres:
        tmp = {
            'model': 'movies.genre',
            'pk': genre['id'],
            'fields': {
                'name': genre['name']
            }
        }
        genre_data.append(tmp)

    with open('tmdb.json','w', encoding='UTF-8') as file:
        json.dump(genre_data, file, ensure_ascii=False, indent=4)

        
def create_movie_id():
    movies_id = []
    for page in range(1, 501):
        print(page)
        url = get_movie_popular_url(page=page)
        raw_data = requests.get(url)
        json_data = raw_data.json()
        movies = json_data.get('results')
        for movie in movies:
            movies_id.append(movie['id'])
    return movies_id

def create_movie_data():
    with open('tmdb.json', 'r+', encoding="UTF-8") as file:
        movie_data = json.load(file)

    # id 값 기준으로 detail 저장, provider도 같이 저장.
    for movie_id in movies_id:
        url = get_details_url(movie_id)
        raw_data = requests.get(url)
        movie = raw_data.json()
        if not movie['poster_path']:
            continue
        genres = movie.pop('genres')
        temp = []
        for i in range(len(genres)):
            temp.append(genres[i]['id'])
        movie['genres'] = temp
        # lst = create_actor(movie_id)
        actors, directors = create_actor(movie_id)
        tmp = {
            'model' : 'movies.movie',
            'pk': movie.pop('id'),
            'fields': {
                'adult': movie['adult'],
                'genres': movie['genres'],
                'original_language': movie['original_language'],
                'original_title': movie['original_title'],
                'overview': movie['overview'],
                'poster_path': 'https://image.tmdb.org/t/p/w300'+ movie['poster_path'],
                'release_date': movie['release_date'],
                'runtime': movie['runtime'],
                'status': movie['status'],
                'title': movie['title'],
                'vote_average': round(movie['vote_average'] / 2, 1),
                'vote_count': movie['vote_count'],
                'actors': actors,
                'directors': directors,
            }
        }
        movie_data.append(tmp)
        
    with open('tmdb.json','w', encoding='UTF-8') as file:
        json.dump(movie_data, file, ensure_ascii=False, indent=4)

def create_movie_provider():
    with open('tmdb.json', 'r+', encoding="UTF-8") as file:
        movie_data = json.load(file)
    privider_data = []
    for movie_id in movies_id:
        url_provider = get_watch_providers(movie_id)
        raw_data = requests.get(url_provider)
        json_data = raw_data.json().get('results')
        if 'KR' not in json_data:
            continue
        provider = json_data['KR']
        temp_flatrate = ''
        if 'flatrate' in provider:
            for i in range(len(provider['flatrate'])):
                temp_flatrate += str(provider['flatrate'][i]['provider_name'])
                temp_flatrate += ','
        temp_buy = ''
        if 'buy' in provider:
            for i in range(len(provider['buy'])):
                temp_buy += str(provider['buy'][i]['provider_name'])
                temp_buy += ','
        temp_rent = ''
        if 'rent' in provider:
            for i in range(len(provider['rent'])):
                temp_rent += str(provider['rent'][i]['provider_name'])
                temp_rent += ','
                
        tmp = {
            'model': 'movies.provider',
            'pk': movie_id,
            'fields' : {
                'flatrate': temp_flatrate,
                'buy': temp_buy,
                'rent': temp_rent,
            }
        }
        
        privider_data.append(tmp)

    with open('tmdb.json','w', encoding='UTF-8') as file:   
        json.dump(privider_data, file, ensure_ascii=False, indent=4).encode('utf8')
        
def create_actor(movie_id):
    
    url = base_url + f'/movie/{movie_id}/credits?api_key={apiKey}&language=ko-KR'
    r_data = requests.get(url)
    # j_data = r_data.json().get('cast')
    j_data = r_data.json()
    actors = []
    directors = []
    actor_data = j_data.get('cast')
    for actor in actor_data:
        if not actor['profile_path']:
                actor['profile_path'] = ""
        tmp = {
            'model': 'movies.actor',
            'pk': actor['id'],
            'fields': {
                'name': actor['name'],
                'profile_path': actor['profile_path']
            }
        }
        actors.append(actor['id'])
        actors_directors_data.append(tmp)

    director_data = j_data.get('crew')
    for director in director_data:
        if director['job'] == 'Director':
            if not director['profile_path']:
                director['profile_path'] = ""
            tmp = {
                'model': 'movies.director',
                'pk': director['id'],
                'fields' : {
                    'name': director['name'],
                    'profile_path': director['profile_path'],
                }
            }
            directors.append(director['id'])
        
            actors_directors_data.append(tmp)

    return actors, directors

movies_id = create_movie_id()
create_genre_data()
create_movie_data()

with open('tmdb.json', 'r+', encoding="UTF-8") as file:
    movie_data = json.load(file)
totaldata = movie_data + actors_directors_data
with open('tmdb.json', 'w', encoding="UTF-8") as file:
    json.dump(totaldata, file, ensure_ascii=False, indent=4)

# create_movie_provider()





    
