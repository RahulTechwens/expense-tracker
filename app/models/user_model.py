from mongoengine import Document, StringField, BooleanField, ObjectIdField

class User(Document):
    phone = StringField(required=False)
    status = BooleanField(required=False)

class Otp(Document):
    otp_val = StringField(required=False)
    verify_status = BooleanField(required=False)
    user_id = ObjectIdField(required=False)
