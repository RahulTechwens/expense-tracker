from mongoengine import Document, StringField, BooleanField, ListField, DictField,FloatField # type: ignore
from pydantic import BaseModel
class Goal(Document):
    title = StringField(required=True)
    description = StringField(required=False)
    target_date = StringField(required=True)
    target_amount = FloatField(required=True)
    status = BooleanField(required=False, default=False)
    user_phone = StringField(required=False)
    created_at= StringField(required=False)
    meta = {
        'collection': 'goals'
    }
    
class Savings(Document):
    parent_goal_id = StringField(required=True)
    entry_amount = FloatField(required=True)
    entry_date = StringField(required=True)
    user_phone = StringField(required=False)
    meta = {
        'collection': 'savings_entry'
    }

    