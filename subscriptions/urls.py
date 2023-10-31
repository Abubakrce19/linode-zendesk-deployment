from django.urls import path, include, re_path
from . import views
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib.staticfiles.urls import static
from django.conf import settings

app_name = 'subscriptions'

urlpatterns = [
    path('upgrade/',  views.Upgrade.as_view(), name='upgrade'),
    path('config/', views.StripeConfig.as_view() , name='config'),
    path('create-checkout-session/', views.Create_checkout_session.as_view(), name='create-checkout-session'),
    path('success/', views.Success.as_view(), name='success'),
    path('cancel/', views.Cancel.as_view() , name='cancel'),
    path('webhook/', views.Stripe_webhook.as_view(), name='webhook'),
]
