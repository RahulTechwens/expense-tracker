import random
import secrets
import time
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "expense"

class OtpHelper:
    # OTP_EXPIRATION_TIME = 10000
    @staticmethod
    def generate_token(phone):
        salt = secrets.token_hex(16)
        # current_time = datetime.utcnow()
        # expires_at = current_time + timedelta(seconds=OtpHelper.OTP_EXPIRATION_TIME)
        payload = {
            "phone": phone,
            # "salt": salt,
            # "exp": expires_at
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        return token

    
    @staticmethod
    def is_token_valid(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            return payload
        except jwt.ExpiredSignatureError:
            print("jwt expired")
            return False
        except jwt.InvalidTokenError:
            print("invald token")
            return False
