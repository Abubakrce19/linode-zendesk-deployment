from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    login_view,
    logout_view,
    forgot_password_view,
    registeration_view,
    check_otp_view,
    check_reset_otp_view,
    reset_new_password_view,
)

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    path('sign_in/', login_view, name='sign_in'),
    path('logout/', logout_view, name='logout'),
    path('sign_up/', registeration_view, name='sign_up'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('activate-email/', check_otp_view, name='activate_email'),
    path('reset-code/', check_reset_otp_view, name='reset_code'),
    path('new-password/', reset_new_password_view, name='reset_new_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
