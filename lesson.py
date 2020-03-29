from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship

Base = declarative_base()


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship('Writer', back_populates='post')

    def __init__(self, title, url, writer):
        self.title = title
        self.url = url
        self.writer = writer

    def __str__(self):
        return f'{self.title} - {self.url}'


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', back_populates='writer')

    def __init__(self, name, url):
        self.name = name
        self.url = url


if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.orm.session import Session

    engine = create_engine('sqlite:///gb_blog.db')
    Base.metadata.create_all(engine)
    session_db = sessionmaker(bind=engine)

    session = session_db()

    post = Post('Первый пост2')
    session.add(post)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()

    print(1)

    pass
import requests
import json
import bs4
from pymongo import MongoClient

headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0'}
URL = 'https://geekbrains.ru/posts'
BASE_URL = 'https://geekbrains.ru'


def get_next_page(soap: bs4.BeautifulSoup) -> str:
    ul = soap.find('ul', attrs={'class': 'gb__pagination'})
    a = ul.find(lambda tag: tag.name == 'a' and tag.text == '›')
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
    template_data = {'url': '',
                     'title': '',
                     'tags': [],
                     'writer': {'name': '',
                                'url': ''}
                     }

    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['url'] = post_url
    template_data['title'] = soap.select_one('article h1.blogpost-title').text
    template_data['tags'] = {itm.text: f'{BASE_URL}{itm["href"]}' for itm in soap.select('article a.small')}
    template_data['writer']['name'] = soap.find('div', attrs={'itemprop': 'author'}).text
    template_data['writer']['url'] = f"{BASE_URL}{soap.find('div', attrs={'itemprop': 'author'}).parent['href']}"
    return template_data


def clear_file_name(url: str):
    return url.replace('/', '_')


if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client['gb_blog']

    for_tags = {}

    for soap in get_page(URL):
        posts = get_post_url(soap)
        data = [get_post_data(url) for url in posts]

        db['posts'].insert_many(data)

        for post in data:
            for name, url in post['tags'].items():
                tmp = db['tags'].find_one({'name': name})
                if tmp:
                    continue
                db['tags'].insert({'name': name, 'url': url})



    #     for post in data:
    #         file_name = clear_file_name(post['url'])
    #
    #         for name, url in post['tags'].items():
    #             if not for_tags.get(name):
    #                 for_tags[name] = {'posts': []}
    #             for_tags[name]['url'] = url
    #             for_tags[name]['posts'].append(post['url'])
    #
    #         with open(f'{file_name}.json', 'w') as file:
    #             file.write(json.dumps(post))
    # with open('tags.json', 'w') as file:
    #     file.write(json.dumps(for_tags))
    #     print(1)

def one():
    print(1)

def two():
    print(2)


funks = {
    'One':one,
    'Two':two,
}

stream = 'One'
