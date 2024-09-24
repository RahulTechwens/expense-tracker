from app.db.connection import mongodb
from app.models.user_model import User
from app.helper.otp_helper import OtpHelper
import random

class AuthService:
    async def sign_up(request_data):
        phone = request_data.get("phone")
        
        
        check_user = User.objects(phone=phone).first()
        if check_user:
          pass
        else:
            otp = random.randint(100000, 999999)
            create_otp = otp(
                
            ) 
        generate_otp = OtpHelper.send_otp(phone)
        
        
        # if(getUserId):
            
        #     token = "rahul"
        # else:
        #     token = "sabui"
            
        # print(token)
        # new_user = User(
        #         phone=phone,
        #         status=True
        #     )
        # new_user.save()
        return {
            "message": "User created successfully",
            "user": {
                "id": str(new_user.id),
                "phone": new_user.phone,
                "status": new_user.status
            }
        }