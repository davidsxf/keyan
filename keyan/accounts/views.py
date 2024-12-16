from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .dingtalk import DingTalkAPI
import json

def dingtalk_login(request):
    """钉钉登录入口"""
    dingtalk = DingTalkAPI()
    auth_url = dingtalk.get_auth_url()
    return redirect(auth_url)

@csrf_exempt
def dingtalk_callback(request):
    """钉钉登录回调处理"""
    code = request.GET.get('code')
    if not code:
        return render(request, 'accounts/login.html', {'error': '未获取到授权码'})

    try:
        dingtalk = DingTalkAPI()
        # 获取访问令牌
        token_info = dingtalk.get_access_token(code)
        print(f"Token Info: {json.dumps(token_info, ensure_ascii=False)}")
        access_token = token_info.get('accessToken')
        
        if not access_token:
            raise ValueError("No access token in response")
        
        # 获取用户信息
        user_info = dingtalk.get_user_info(code)  # 使用code而不是access_token
        print(f"User Info: {json.dumps(user_info, ensure_ascii=False)}")
        
        # 从用户信息中获取必要字段
        user_info = user_info.get('user_info', {})  # SNS API 返回的用户信息在 user_info 字段中
        
        # 获取用户标识
        unionid = (user_info.get('unionid') or  # SNS API 返回的是小写的 unionid
                  user_info.get('openid') or 
                  token_info.get('unionId') or 
                  token_info.get('openId'))
        
        if not unionid:
            raise ValueError("No user identifier found in response")
        
        # 获取用户昵称
        nick = (user_info.get('nick') or 
               user_info.get('nickname') or 
               user_info.get('name') or
               f"DingTalk_{unionid[:8]}")  # 使用 unionid 前8位作为后备
        
        # 获取或创建用户
        username = f"dingtalk_{unionid}"  # 添加前缀避免冲突
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': nick,
                'is_active': True
            }
        )
        
        # 更新用户昵称（如果有变化）
        if not created and user.first_name != nick:
            user.first_name = nick
            user.save()
        
        # 登录用户
        login(request, user)
        return redirect('dashboard:index')
        
    except Exception as e:
        error_message = str(e)
        print(f"Login Error: {error_message}")
        return render(request, 'accounts/login.html', {'error': error_message})
