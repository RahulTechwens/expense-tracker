from mongoengine import Document, StringField, BooleanField, ListField, DictField # type: ignore
class Alert(Document):
    alert_type = StringField(required=False)
    alert_data = ListField(DictField())
    limit = StringField(required=False)
    cat_ids = ListField(required=False)
    status = BooleanField(required=False)