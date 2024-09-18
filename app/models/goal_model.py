from mongoengine import Document, StringField, BooleanField, ListField, DictField,FloatField # type: ignore
from pydantic import BaseModel
class Goal(Document):
    title = StringField(required=True)
    description = StringField(required=False)
    target_date = StringField(required=True)
    target_amount = FloatField(required=True)
    meta = {
        'collection': 'goals'
    }
    
class Savings(Document):
    parent_goal_id = StringField(required=True)
    entry_amount = FloatField(required=True)
    entry_date = StringField(required=True)
    meta = {
        'collection': 'savings_entry'
    }

    