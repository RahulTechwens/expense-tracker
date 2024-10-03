from mongoengine import Document, StringField, BooleanField, ObjectIdField, DateTimeField
from datetime import datetime, timedelta

class User(Document):
    phone = StringField(required=False)
    status = BooleanField(required=False)
    is_new_user = BooleanField(required=False)

class Otp(Document):
    otp_val = StringField(required=False)
    verify_status = BooleanField(required=False)
    phone = StringField(required=False)
    expire_at = DateTimeField(default=datetime.utcnow() + timedelta(minutes=5))  # Set TTL for 5 minutes

    meta = {
        'indexes': [
            {'fields': ['expire_at'], 'expireAfterSeconds': 0}  # TTL index
        ]
    }