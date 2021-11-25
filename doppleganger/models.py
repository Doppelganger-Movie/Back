from django.db import models
from django.conf import settings
import os

def user_directory_path(instance, filename):
    return 'users/{0}/{1}'.format(instance.upload_user.username, filename)  # user를 upload_user로 저장했기 때문에 instance.upload_user로 사용함

def user_path(instance):
    return 'users/{0}'.format(instance.upload_user.username)


class SelfImage(models.Model):
    upload_date = models.DateTimeField(auto_now_add=True) # 업로드 시간
    upload_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 업로드 유저
    upload_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True) # 이미지 경로
    def delete(self, *args, **kargs):   # DB 를 삭제하면 저장한 이미지도 삭제되도록 하기 위해
        if self.upload_image:
            img_path = f'{settings.MEDIA_ROOT}/{user_path}'
            os.remove(os.path.join(img_path, self.upload_image.path))
        super(SelfImage, self).delete(*args, **kargs)
