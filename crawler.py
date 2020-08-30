import requests
import datetime
from bs4 import BeautifulSoup
from models import PortalNews

NAVER_SECTIONS = {
    '100': '정치',
    '101': '경제',
    '102': '사회',
    '103': '생활/문화',
    '104': '세계',
    '105': 'IT/과학'
}

DAUM_SECTIONS = {
    'news': '뉴스',
    'entertain': '연예',
    'sports': '스포츠'
}

NAVER_RANKING_NEWS_URL = 'https://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&sectionId='
DAUM_RANKING_NEWS_URL = 'https://news.daum.net/ranking/popular/'
DEFAULT_TIMEOUT = 10
DEFAULT_HEADER = {
    'User-Agent': 'Mozilla/5.0'
}

MAX_NEWS_LEN = 20


def naver_news_crawler(section):
    title_list = list()
    created_at = datetime.datetime.utcnow().isoformat()[:19]

    try:
        naver_url = f'{NAVER_RANKING_NEWS_URL}{section}'
        naver_resp = requests.get(naver_url, headers=DEFAULT_HEADER)
        naver_soup = BeautifulSoup(naver_resp.text, 'html.parser')

        for i, tag in enumerate(naver_soup.find_all('div', {'class': 'ranking_headline'})[:MAX_NEWS_LEN]):
            title = tag.get_text().strip()
            title_list.append({'rank': i+1, 'title': title})

        if title_list:
            news_item = PortalNews('naver', createdAt=created_at, section=NAVER_SECTIONS[section], news=title_list)
            news_item.save()
        else:
            raise Exception(f'Naver no title: {section}')

    except Exception as e:
        print(f'ERROR: {e}')
        return None

    return title_list


def daum_news_crawler(section):
    title_list = []
    created_at = datetime.datetime.utcnow().isoformat()[:19]

    try:
        daum_url = f'{DAUM_RANKING_NEWS_URL}{section}'
        daum_resp = requests.get(daum_url)
        daum_soup = BeautifulSoup(daum_resp.text, 'html.parser')

        for i, tag in enumerate(daum_soup.find_all('li', {'data-tiara-layer': 'news_list'})[:MAX_NEWS_LEN]):
            title = tag.find('a', 'link_txt').get_text().strip()
            title_list.append({'rank': i+1, 'title': title})

        if title_list:
            news_item = PortalNews('daum', createdAt=created_at, section=DAUM_SECTIONS[section], news=title_list)
            news_item.save()
        else:
            raise Exception(f'Daum no title: {section}')

    except Exception as e:
        print(e)
        return None

    return title_list


def lambda_handler(event, context):
    naver_results = {v: naver_news_crawler(k) for k, v in NAVER_SECTIONS.items()}
    daum_results = {v: daum_news_crawler(k) for k, v in DAUM_SECTIONS.items()}

    # print(naver_results)
    # print(daum_results)

    if all(naver_results.values()) and all(daum_results.values()):
        return 'success'
    else:
        return 'error'
