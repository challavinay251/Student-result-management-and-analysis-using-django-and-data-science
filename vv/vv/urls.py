from django.contrib import admin
from django.urls import path,include
from app import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path
from app.views import upload_excel,excel_data
from app.views import upload_excel,marksheet,respones
from app import views
from app.views import send_rank_emails



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('special/', views.special, name='special'),
    path('app/', include('app.urls')),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('upload_excel/', upload_excel, name='upload_excel'),
    path('result/', excel_data, name='view_excel'),
    path('marksheet/', marksheet, name='marksheet'),
    path('respones/', respones, name='respones'),
    path('analysis-results/', views.analyze_data, name='analyze_data'),
    path('send-rank-emails/', send_rank_emails, name='send_rank_emails'),

   ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
