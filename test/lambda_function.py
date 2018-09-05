import json
import urllib.request


def request_naver():
    with urllib.request.urlopen('http://naver.com') as response:
        naver_html = response.read()

        return naver_html.decode('utf-8')


def lambda_handler(event, context):
    return request_naver()


