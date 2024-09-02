from mongoengine import Document, StringField, IntField, BooleanField, ListField, FloatField, DateTimeField # type: ignore
import datetime

class Expense(Document):
    cat = StringField(required=True)
    merchant = StringField(required=True)
    acct = StringField(required=True)
    bank = StringField(required=True)
    date = StringField(required=True)
    # date = DateTimeField(default=datetime.datetime.time)
    body = StringField()
    amount = IntField(required=True)
    type = StringField(required=True)
    method = StringField(required=True)
    manual = BooleanField(required=True)
    keywords = ListField(StringField(), default=[])
    vector = ListField(FloatField(), default=[])
    meta = {
        'collection': 'demo_sms_data'
    }