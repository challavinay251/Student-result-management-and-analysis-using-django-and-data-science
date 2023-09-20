from django.contrib import admin
from app.models import User,UserProfileInfo
# Register your models here.
admin.site.register(UserProfileInfo)

from django.contrib import admin
from app.models import ExcelFile
# Register your models here.
admin.site.register(ExcelFile)