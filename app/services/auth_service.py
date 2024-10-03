import random
from app.models.user_model import User, Otp
from app.helper.otp_helper import OtpHelper

class AuthService:
    @staticmethod
    def generate_otp(phone):
        """ Helper function to generate and save OTP """
        # otp = random.randint(100000, 999999)
        otp = 111111
        new_otp = Otp(
            otp_val=str(otp),
            verify_status=False,
            phone=phone
        )
        new_otp.save()
        return otp

    @staticmethod
    async def send(request_data):
        """ Send OTP to a user, creating them if they don't exist """
        phone = request_data.get("phone")
        if not phone:
            return {"message": "Phone number is required.", "data": None}

        check_user = User.objects(phone=phone).first()

        if not check_user:
            # Create a new user if they don't exist
            new_user = User(phone=phone, status=True,  is_new_user = True)
            new_user.save()

        # Generate and save a new OTP
        otp = AuthService.generate_otp(phone)

        return {
            "message": "OTP sent successfully",
            "data": {
                "otp": otp,
                "phone": phone
            }
        }

    @staticmethod
    async def verify(request_data):
        """ Verify the OTP and return token if valid """
        otp = request_data.get("otp")
        phone = request_data.get("phone")

        if not phone or not otp:
            return {"status": False, "message": "Phone number and OTP are required."}

        # Check if OTP exists for the provided phone
        check_otp = Otp.objects(phone=phone).first()

        
        if check_otp and check_otp.otp_val == otp:
            # OTP matches, generate token
            token = OtpHelper.generate_token(phone)

            check_user = User.objects(phone=phone).first()
            is_new_user = check_user.is_new_user
            # For first time login the is_new_user flag will True for the next time it will be set to False
            check_user.update(is_new_user=False)
            
            # No need to manually delete the OTP because TTL will expire it
            return {
                "status": True,
                "message": "OTP verified successfully.",
                "token": token,
                "is_new_user":is_new_user
            }

        return {
            "status": False,
            "message": "Wrong OTP provided!"
        }

    @staticmethod
    async def verify_token(token):
        """ Verify token validity using OtpHelper """
        if not token:
            return {"status": False, "message": "Token is required."}

        token_valid = OtpHelper.is_token_valid(token)

        return {
            "status": token_valid,
            "message": "Token is valid." if token_valid else "Token is invalid."
        }

    @staticmethod
    async def resend_otp(request_data):
        """ Resend OTP by creating a new one (old OTP will expire automatically via TTL) """
        phone = request_data.get("phone")
        if not phone:
            return {"message": "Phone number is required.", "data": None}

        # Generate and send a new OTP
        otp = AuthService.generate_otp(phone)

        return {
            "message": "OTP sent successfully",
            "data": {
                "otp": otp,
                "phone": phone
            }
        }