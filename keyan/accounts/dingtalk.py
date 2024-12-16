import requests
from django.conf import settings
from django.core.exceptions import ValidationError
import json
import time
import hmac
import hashlib
import base64

class DingTalkAPI:
    def __init__(self):
        self.app_key = settings.DINGTALK_APP_KEY
        self.app_secret = settings.DINGTALK_APP_SECRET
        self.redirect_uri = settings.DINGTALK_REDIRECT_URI

    def get_auth_url(self):
        """获取钉钉登录授权URL"""
        return (
            f"https://login.dingtalk.com/oauth2/auth?"
            f"client_id={self.app_key}&"
            f"response_type=code&"
            f"scope=openid&"
            f"prompt=consent&"
            f"state=STATE&"
            f"redirect_uri={self.redirect_uri}"
        )

    def get_access_token(self, code):
        """使用授权码获取访问令牌"""
        url = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
        data = {
            "clientId": self.app_key,
            "clientSecret": self.app_secret,
            "code": code,
            "grantType": "authorization_code"
        }
        response = requests.post(url, json=data)
        if response.status_code != 200:
            raise ValidationError(f"Failed to get access token: {response.text}")
        return response.json()

    def get_user_info(self, access_token):
        """获取用户信息"""
        try:
            # 使用 sns getuserinfo_bycode 接口
            timestamp = str(int(time.time() * 1000))
            signature = self._compute_signature(timestamp)
            
            url = "https://oapi.dingtalk.com/sns/getuserinfo_bycode"
            params = {
                "accessKey": self.app_key,
                "timestamp": timestamp,
                "signature": signature
            }
            data = {
                "tmp_auth_code": access_token
            }
            
            response = requests.post(url, params=params, json=data)
            
            if response.status_code != 200:
                error_msg = f"Failed to get user info: {response.text}"
                print(f"DingTalk API Error: {error_msg}")
                raise ValidationError(error_msg)
            
            user_info = response.json()
            print(f"DingTalk API Response: {json.dumps(user_info, ensure_ascii=False)}")
            return user_info
            
        except Exception as e:
            print(f"DingTalk API Exception: {str(e)}")
            raise ValidationError(f"Error getting user info: {str(e)}")
    
    def _compute_signature(self, timestamp):
        """计算签名"""
        message = timestamp + "\n" + self.app_secret
        hmac_code = hmac.new(
            self.app_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(hmac_code).decode('utf-8')