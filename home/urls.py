from django.contrib import admin
from django.urls import path, include
from home import views
from .views import predict

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('predict/', views.predict, name='predict'),
    path('send_email/', views.send_email, name='send_email'),
]