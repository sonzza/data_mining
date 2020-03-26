import requests
import json
import bs4
from pymongo import MongoClient
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship


headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.122 Safari/537.36'}
URL = 'https://habr.com/ru/top/weekly/'
BASE_URL = 'https://habr.com/'


def get_next_page(soap: bs4.BeautifulSoup) -> str:
    #ul = soap.find('div.page_footer', attrs={'id': 'next_page'})
    a = soap.find(lambda tag: tag.name == 'a' and tag.text == 'туда')
    return f'{BASE_URL}{a["href"]}' if a else None


def get_post_url(soap: bs4.BeautifulSoup) -> set:
    post_a = soap.select('div.post-items-wrapper div.post-item a')
    return set(f'{BASE_URL}{a["href"]}' for a in post_a)


def get_page(url):
    while url:
        print(url)
        response = requests.get(url, headers=headers)
        soap = bs4.BeautifulSoup(response.text, 'lxml')
        yield soap
        url = get_next_page(soap)


def get_post_data(post_url: str) -> dict:
    template_data = {'title': '',
                     'url': '',
                     'coment_count': '',
                     'public_time': '',
                     'writer': {'name': '',
                                'url': ''},
                     'comment_writters': {'name': '',
                                'url': ''}
                     }

    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['title'] = soap.select_one('a.post__title_link').text
    template_data['tags'] = {itm.text: f'{itm["href"]}' for itm in soap.select_one('a.inline-list__item-link').text}
    template_data['url'] = post_url
    template_data['image'] = soap.find('div').img['src']
    template_data['writer']['name'] = soap.find('div', attrs={'itemprop': 'author'}).text
    template_data['writer']['url'] = f"{BASE_URL}{soap.find('div', attrs={'itemprop': 'author'}).parent['href']}"
    return template_data


if __name__ == '__main__':
    get_next_page(URL)