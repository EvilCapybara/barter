"""
URL configuration for barter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('ads/create/', views.create_ad, name='create_ad'),
    path('ads/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ads/<int:pk>/delete/', views.delete_ad, name='delete_ad'),
    path('ads/<int:pk>/edit/', views.edit_ad, name='edit_ad'),
    path('ads/', views.search_and_filter_ads, name='ads_list'),
    path('exchange/create/', views.create_exchange_offer, name='create_exchange_offer'),
    path('exchange/my_offers/', views.filter_offers, name='my_offers'),
    path('exchange/my_offers/respond/<int:offer_id>/', views.respond_offer, name='respond_offer'),


]

handler404 = 'barter.views.custom_404_view'
