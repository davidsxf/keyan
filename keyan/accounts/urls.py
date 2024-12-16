from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dingtalk/login/', views.dingtalk_login, name='dingtalk_login'),
    path('dingtalk/callback/', views.dingtalk_callback, name='dingtalk_callback'),
] 