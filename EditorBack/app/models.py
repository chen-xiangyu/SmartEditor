from django.db import models
from django.utils import timezone
import os.path
from django.conf import settings
# Create your models here.

class User(models.Model):
    name = models.CharField(verbose_name="用户名", max_length=64)
    account = models.CharField(verbose_name="账号", max_length=64, unique=True)
    password = models.CharField(verbose_name="密码", max_length=128)
    accessToken = models.CharField(verbose_name="访问令牌", max_length=128, null=True)
    coins = models.IntegerField(verbose_name="硬币数量", default=0)

    def __str__(self):
        return self.name
def file_directory_path(instance, filename):
    # 文件将上传到 MEDIA_ROOT/user_<creator_id>/<filename>
    return os.path.join(f'user_{instance.creator.id}', filename)

class File(models.Model):
    name = models.CharField(verbose_name="文件名", max_length=128)
    created_time = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    last_modified = models.DateTimeField(verbose_name="最近修改时间", auto_now=True)
    creator = models.ForeignKey(User, related_name='created_files', on_delete=models.CASCADE, verbose_name="创建者")
    file = models.FileField(upload_to=file_directory_path)
    shared_with = models.ManyToManyField(User, related_name='shared_files', verbose_name="共享用户")

    def __str__(self):
        return self.name
    def get_file_path(self):
        return os.path.join(settings.MEDIA_ROOT, str(self.file))
