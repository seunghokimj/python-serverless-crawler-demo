from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute


class PortalNews(Model):
    class Meta:
        table_name = "PortalNews"
        region = 'ap-northeast-2'

    portal = UnicodeAttribute(hash_key=True)
    createdAt = UnicodeAttribute(range_key=True)
    section = UnicodeAttribute()
    news = ListAttribute()
