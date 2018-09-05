import datetime
import requests
from bs4 import BeautifulSoup
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute


class PortalKeyword(Model):
    """
    A DynamoDB Keyword
    """
    class Meta:
        table_name = "PortalKeyword"
        region = 'ap-northeast-2'

    portal = UnicodeAttribute(hash_key=True)
    createdAt = UnicodeAttribute(range_key=True)
    keywords = ListAttribute()


def lambda_handler(event, context):
    created_at = datetime.datetime.utcnow().isoformat()[:19]

    naver_keywords = []

    naver_resp = requests.get('https://www.naver.com/')
    naver_soup = BeautifulSoup(naver_resp.text, 'html.parser')

    try:
        for ah_item in naver_soup.select('.ah_item')[:20]:
            rank = int(ah_item.select('.ah_r')[0].get_text())
            keyword = ah_item.select('.ah_k')[0].get_text()

            naver_keywords.append({'rank': rank, 'keyword': keyword})

        keyword_item = PortalKeyword('naver', created_at)
        keyword_item.keywords = naver_keywords
        keyword_item.save()

    except Exception as e:
        print(e)
        return 'error'

    return 'success'
