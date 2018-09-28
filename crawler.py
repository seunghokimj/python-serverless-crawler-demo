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


def naver_keywords_crawler():
    created_at = datetime.datetime.utcnow().isoformat()[:19]
    naver_keywords = []

    try:
        naver_resp = requests.get('https://www.naver.com/')
        naver_soup = BeautifulSoup(naver_resp.text, 'html.parser')

        for i, tag in enumerate(naver_soup.find_all('span', {'class':'ah_k'})[:20]):
            rank = i+1
            keyword = tag.get_text()

            naver_keywords.append({'rank': rank, 'keyword': keyword})

        keyword_item = PortalKeyword('naver', created_at)
        keyword_item.keywords = naver_keywords
        keyword_item.save()

    except Exception as e:
        print(e)
        return None

    return naver_keywords


def daum_keywords_crawler():
    created_at = datetime.datetime.utcnow().isoformat()[:19]
    daum_keywords = []

    try:
        daum_resp = requests.get('https://www.daum.net/')
        daum_soup = BeautifulSoup(daum_resp.text, 'html.parser')

        for i, tag in enumerate(daum_soup.find_all('a', {'class': 'link_issue', 'tabindex': '-1'})):
            rank = i+1
            keyword = tag.get_text()

            daum_keywords.append({'rank': rank, 'keyword': keyword})

        keyword_item = PortalKeyword('daum', created_at)
        keyword_item.keywords = daum_keywords
        keyword_item.save()

    except Exception as e:
        print(e)
        return None

    return daum_keywords


def lambda_handler(event, context):

    naver_result = naver_keywords_crawler()
    daum_result = daum_keywords_crawler()

    # print(naver_result)
    # print(daum_result)

    if naver_result and daum_result:
        return 'success'
    else:
        return 'error'
