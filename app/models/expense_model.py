from mongoengine import Document, StringField, IntField, BooleanField, ListField, FloatField, DateTimeField # type: ignore
import datetime

class Expense(Document):
    cat = StringField(required=True)
    merchant = StringField(required=True)
    merchant_slug = StringField(required=False)
    acct = StringField(required=True)
    bank = StringField(required=True)
    date = StringField(required=True)
    # date = DateTimeField(default=datetime.datetime.time)
    body = StringField()
    amount = FloatField(required=True)
    type = StringField(required=True)
    method = StringField(required=True)
    manual = BooleanField(required=True)
    keywords = ListField(StringField(), default=[])
    vector = ListField(FloatField(), default=[])
    meta = {
        'collection': 'demo_sms_data'
    }
    
    
class Cat(Document):
    icon_id = IntField(required=True)
    label = StringField(required=True)
    type = StringField(required=True)
    color_code = StringField(required=False)
    meta = {
        'collection': 'categories'
    }
    

# class CustomCat(Document):
#     icon_id = IntField(required=True)
#     label = StringField(required=True)
#     parent_genre_id = StringField(required=True)
#     meta = {
#         'collection': 'custom_categories'
#     }
    
    
    
class Message(Document):
    msg = StringField(required=True)

    
    