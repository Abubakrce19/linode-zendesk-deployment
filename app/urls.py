from django.urls import path, include, re_path
from . import views
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib.staticfiles.urls import static
from django.conf import settings
from django.views.static import serve

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

app_name = 'app'

urlpatterns = [    
    path('onboard/', views.Onboard.as_view(), name="onboard"),
    path('dashboard/<str:id>/', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/', views.Dashboard.as_view(), name="dashboard"),    
    path('api/setup_user/', views.Setup_user.as_view(), name="setup_user"),
    path('api/chat/', views.Chat.as_view(), name="chat"),
    path('api/update_db/', views.Update_db.as_view(), name="update_db"),
    path('user_profile/', views.UserProfile.as_view(), name="user_profile"),
    path('update_profile/', views.Update_profile.as_view(), name='update_profile'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)