from mongoengine import Document, StringField, IntField, BooleanField, ListField, FloatField, DateTimeField # type: ignore
 
class Alert(Document):
    alert_type = StringField(required=False)
    limit = StringField(required=False)
    