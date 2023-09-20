from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    portfolio_site = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)
def __str__(self):
  return self.user.username

from django.db import models
class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_files/')
    name = models.CharField(max_length=255,null=True)
    date = models.DateField()
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True)

