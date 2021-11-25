from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from requests.api import request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import render, get_list_or_404, get_object_or_404
from .models import SelfImage
from movies.models import Movie
from .serializers import SelfImageSerializer
from django.core.files import File as DjangoFile
from decouple import config
import requests
from django.http import JsonResponse
import urllib.request
import json
from movies.serializers import MovieSerializer
import pandas as pd
from pandas import Series, DataFrame
import sqlite3
from .serializers import SelfImageSerializer



client_id = config('client_id')
client_secret = config('client_secret')
naver_serach_id = config('naver_serach_id')
naver_search_secret = config('naver_search_secret')

# 1번 함수
# 사용자가 이미지를 업로드 했을 때
# 도플갱어를 찾고
# 그 값을 DB에 업데이트
# 프론트로 보내주기
@api_view(['POST'])
def analyze_image(request):
    if request.user.is_authenticated:
        src = request.FILES['files'] # 파일이 하나일 경우
        #for img in request.FILES.getlist('files'):   # 파일이 여러개일 경우
        #    upload_img = UploadImage.objects.create(image=img, .....)
        # print(image_instance)

        # url = request
        # print('명령은 이렇게 들어옴')
        # print(url)
        
        image_instance = SelfImage.objects.create(upload_image=src, upload_user=request.user)

        serializer = SelfImageSerializer(image_instance)
        return Response(serializer.data)

        # print(request.user.username)
        # data = {
        #     'upload_user' : request.user.username
        # }
        # return JsonResponse(data)



# 2번 함수
# 사용자가 저장해둔 마지막 도플갱어 정보를 가져오기.
@api_view(['GET'])
def get_doppleganger(request,user_id):

    # DB -> 필요한 정보 빼와서 읽기
    con = sqlite3.connect("db.sqlite3")
    query = 'select * from DoppleList_{} where upload_userid = "{}"'.format(request.user.username, user_id)
    dr = pd.read_sql(query, con = con)
    # print(dr)
    # print(type(dr))

    # DataFrame -> json
    result = dr.to_json(orient="records")
    parsed = json.loads(result)
    # print(parsed)
    # print(type(parsed))
    data = {
    'info' : parsed
    }
    # json.dumps(parsed, indent = 4)

    # # DB에서 지우기(이거면 업데이트도 가능할듯!!)
    # conn = sqlite3.connect("db.sqlite3")
    # cur = conn.cursor()
    # cur.execute('DROP TABLE DoppleList')
    # print('Drop 성공')
    # conn.commit()
    # conn.close

    return JsonResponse(data)

        






# 3번 함수(1번에서 사용.)
# 사용자의 마지막 사진 정보를 입력받아
# 같은 pk의 도플갱어 정보 필드에 도플갱어 정보를 저장.
@api_view(['GET', 'POST'])
def doppleganger(request):
    cfr_url = "https://naveropenapi.apigw.ntruss.com/vision/v1/celebrity"
    uploaded_imgs = SelfImage.objects.filter(upload_user=request.user).values('upload_image') #업로드한 이미지 주소 모두 불러와 리스트에 넣고 그 리스트의 [length-1]번(가장 최근)
    if len(uploaded_imgs) > 0:
        image_path = uploaded_imgs[len(uploaded_imgs)-1]['upload_image']
        files = {'image': open(f'media/{image_path}', 'rb')}
        headers = {'X-NCP-APIGW-API-KEY-ID': client_id, 'X-NCP-APIGW-API-KEY': client_secret }
        response = requests.post(cfr_url,  files=files, headers=headers)
        
        celeb_list = response.json().get('faces')
        celeb_confidence = 0
        for celeb in celeb_list:
            if celeb['celebrity']['confidence'] > celeb_confidence:
                celeb_confidence = celeb['celebrity']['confidence']
                celeb_name = celeb['celebrity']['value']
        # print('닮은ㅅ사람!',celeb_list )
        # print(celeb_name)
        act_url = 'http://kobis.or.kr/kobisopenapi/webservice/rest/people/searchPeopleList.json?key=f5eef3421c602c6cb7ea224104795888&peopleNm='+celeb_name
        r_data = requests.get(act_url)
        json_data = r_data.json()
        actor_list = json_data['peopleListResult']['peopleList']
        movie_list = []
        # print('엥 왜 더 없어???', json_data['peopleListResult'])
        for actor in actor_list:
            if actor['repRoleNm'] == '배우':
                # print('자르기전', actor['filmoNames'])
                movie_list = actor['filmoNames'].split('|')
                break
            
        encText = urllib.parse.quote(celeb_name)
        # encText = urllib.parse.quote( "나쁜 녀석들: 더 무비")
        serach_url = 'https://openapi.naver.com/v1/search/image?query=' + encText +'&display=1&sort=sim'
        req = urllib.request.Request(serach_url)
        req.add_header("X-Naver-Client-Id",naver_serach_id)
        req.add_header("X-Naver-Client-Secret",naver_search_secret)
        respon = urllib.request.urlopen(req)

        res_body = json.loads(respon.read())

        celeb_movie_poster =[]
        celeb_movie_id = []
        celeb_movie_title = []
        for movie_title in movie_list:
            movie = Movie.objects.filter(title=movie_title.rstrip())
            # movie = Movie.objects.filter(title='스파이더맨 3')
            serializer = MovieSerializer(movie, many=True)
            # print('데이터확인', len(serializer.data))
            if len(serializer.data):
                if len(celeb_movie_poster) == 10:
                    continue
                celeb_movie_poster.append(serializer.data[0]['poster_path'])
                celeb_movie_id.append(serializer.data[0]['id'])
                celeb_movie_title.append(serializer.data[0]['title'])
        # print('moie나오나???!!!!', serializer.data[0]['poster_path'])
        # print(celeb_movie_title)
        
        celeb_img = res_body['items'][0]['link']
        data = {
            #사진 함께 넘겨주기
            'upload_image': image_path,
            'upload_userid':request.user.id,
            'upload_username':request.user.username,
            'celeb': celeb_name,
            'confidence': celeb_confidence,
            'celeb_movie_title': celeb_movie_title,
            'celeb_movie_id': celeb_movie_id,
            'celeb_movie_poster': celeb_movie_poster,
            'celeb_image': celeb_img
        }
        
        # Json -> SQL(DB)
        df = DataFrame(data)
        con = sqlite3.connect("db.sqlite3")
        df.to_sql(f'DoppleList_{request.user.username}', con, if_exists='replace', index=False)
        
        # print('리스트!!', movie_list)
        # print(data)
        # print(type(data))
        # print(JsonResponse(data))
        
        return JsonResponse(data)
    else:
        data= {
            'msg':'사진을 올려주세요.'
        }
        return JsonResponse(data)









# 지원님 작성 원 코드

# @api_view(['GET', 'POST'])
# def doppleganger(request):
#     cfr_url = "https://naveropenapi.apigw.ntruss.com/vision/v1/celebrity"
#     uploaded_imgs = SelfImage.objects.filter(upload_user=request.user).values('upload_image') #업로드한 이미지 주소 모두 불러와 리스트에 넣고 그 리스트의 [length-1]번(가장 최근)
#     if len(uploaded_imgs) > 0:
#         image_path = uploaded_imgs[len(uploaded_imgs)-1]['upload_image']
#         files = {'image': open(f'media/{image_path}', 'rb')}
#         headers = {'X-NCP-APIGW-API-KEY-ID': client_id, 'X-NCP-APIGW-API-KEY': client_secret }
#         response = requests.post(cfr_url,  files=files, headers=headers)
        
#         celeb_list = response.json().get('faces')
#         celeb_confidence = 0
#         for celeb in celeb_list:
#             if celeb['celebrity']['confidence'] > celeb_confidence:
#                 celeb_confidence = celeb['celebrity']['confidence']
#                 celeb_name = celeb['celebrity']['value']
#         # print('닮은ㅅ사람!',celeb_list )
#         # print(celeb_name)
#         act_url = 'http://kobis.or.kr/kobisopenapi/webservice/rest/people/searchPeopleList.json?key=f5eef3421c602c6cb7ea224104795888&peopleNm='+celeb_name
#         r_data = requests.get(act_url)
#         json_data = r_data.json()
#         actor_list = json_data['peopleListResult']['peopleList']
#         movie_list = []
#         # print('엥 왜 더 없어???', json_data['peopleListResult'])
#         for actor in actor_list:
#             if actor['repRoleNm'] == '배우':
#                 # print('자르기전', actor['filmoNames'])
#                 movie_list = actor['filmoNames'].split('|')
#                 break
            
#         encText = urllib.parse.quote(celeb_name)
#         # encText = urllib.parse.quote( "나쁜 녀석들: 더 무비")
#         serach_url = 'https://openapi.naver.com/v1/search/image?query=' + encText +'&display=1&sort=sim'
#         req = urllib.request.Request(serach_url)
#         req.add_header("X-Naver-Client-Id",naver_serach_id)
#         req.add_header("X-Naver-Client-Secret",naver_search_secret)
#         respon = urllib.request.urlopen(req)

#         res_body = json.loads(respon.read())

#         celeb_movie_poster =[]
#         celeb_movie_id = []
#         celeb_movie_title = []
#         for movie_title in movie_list:
#             movie = Movie.objects.filter(title=movie_title.rstrip())
#             # movie = Movie.objects.filter(title='스파이더맨 3')
#             serializer = MovieSerializer(movie, many=True)
#             # print('데이터확인', len(serializer.data))
#             if len(serializer.data):
#                 if len(celeb_movie_poster) == 5:
#                     continue
#                 celeb_movie_poster.append(serializer.data[0]['poster_path'])
#                 celeb_movie_id.append(serializer.data[0]['id'])
#                 celeb_movie_title.append(serializer.data[0]['title'])
#         # print('moie나오나???!!!!', serializer.data[0]['poster_path'])
#         # print(celeb_movie_title)
        
#         celeb_img = res_body['items'][0]['link']
#         data = {
#             'celeb': celeb_name,
#             'confidence': celeb_confidence,
#             'celeb_movie_title': celeb_movie_title,
#             'celeb_movie_id': celeb_movie_id,
#             'celeb_movie_poster': celeb_movie_poster,
#             'celeb_image': celeb_img
#         }
        
#         # print('리스트!!', movie_list)
#         # print(data)
#         # print(type(data))
#         # print(JsonResponse(data))
        
#         return JsonResponse(data)
#     else:
#         data= {
#             'msg':'사진을 올려주세요.'
#         }
#         return JsonResponse(data)