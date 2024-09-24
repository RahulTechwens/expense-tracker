# from app.helper.otp_helper import OtpHelper

# def verify_token(request: Request):
#     token = request.headers.get('Authorization')
#     token = token.split(" ")[1]  # Remove "Bearer" prefix
#     try:
#         get_token = OtpHelper.is_token_valid(token)
#         # user_id: str = payload.get("user_id")
#         # if user_id is None:
#         #     raise credentials_exception
#         # return user_id
#     except JWTError:
#         raise credentials_exception
