import requests
import bs4
from pymongo import MongoClient
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Table
)
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.122 Safari/537.36'}
URL = 'https://habr.com/ru/top/weekly'
BASE_URL = 'https://habr.com'


def get_post_url(soap: bs4.BeautifulSoup) -> set:
    post_a = soap.select('a.post__title_link')
    return set(f'{a["href"]}' for a in post_a)


def get_next_page(soap: bs4.BeautifulSoup) -> str:
    a = soap.find('a', attrs={'id': 'next_page'})
    return f'{BASE_URL}{a["href"]}' if a else None


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
                     'comment_count': '',
                     'public_time': '',
                     'writer': {'name': '',
                                'url': ''},
                     'comment_writers': [{'name': 'url'}]
                     }

    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['title'] = soap.select_one('div.post__wrapper h1 span').text
    template_data['url'] = post_url
    template_data['comment_count'] = soap.select_one('span.comments-section__head-counter',
                                                     attrs={'id': 'comments_count'}).text.replace('\n', '').replace(' ',
                                                                                                                    '')
    template_data['public_time'] = soap.select_one('span.post__time').text
    template_data['writer']['name'] = soap.select_one('span.user-info__nickname').text
    template_data['writer']['url'] = soap.select_one('div.post__wrapper header a')['href']
    comment_writers = {}
    for tag in soap.select('a.user-info_inline'):
        comment_writers[tag['data-user-login']] = tag['href']
    template_data["comment_writers"] = comment_writers
    return template_data


if __name__ == '__main__':
    # Mongo_time
    #     client_mongo = MongoClient('mongodb://127.0.0.1:27017/')
    #     db = client_mongo['habr_top_weekly']
    #
    #     for soap in get_page(URL):
    #         posts = get_post_url(soap)
    #         data = [get_post_data(url) for url in posts]
    #         db['posts'].insert_many(data)
    #         # for post in data:
    #         #     with open('{name}.json'.format(name=post['title'].replace('/', '_')), 'w') as file:
    #         #         file.write(json.dumps(post))

    # SQL_time

    Base = declarative_base()

    association_table = Table('association', Base.metadata,
                              Column('post_id', Integer, ForeignKey('comment_writer.id')),
                              Column('comment_writer_id', Integer, ForeignKey('post.id')))

    class Comment_writer(Base):
        __tablename__ = 'comment_writer'
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, unique=False, nullable=False)
        url = Column(String, unique=True, nullable=False)
        # post = relationship('Post', back_populates='comment_writer')

        def __init__(self, name, url, post):
            self.name = name
            self.url = url
            self.post = post


    class Writer(Base):
        __tablename__ = 'writer'
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, unique=False, nullable=False)
        url = Column(String, unique=True, nullable=False)

        def __init__(self, name, url):
            self.name = name
            self.url = url


    class Post(Base):
        __tablename__ = 'post'
        id = Column(Integer, primary_key=True, autoincrement=True)
        title = Column(String, unique=False, nullable=False)
        url = Column(String, unique=True, nullable=False)
        comment_count = Column(String, unique=False, nullable=True)
        writer_id = Column(Integer, ForeignKey('writer.id'))
        writer = relationship('Writer', backref='post')
        comment_writer = relationship('Comment_writer',  secondary=association_table)

        def __init__(self, title, url, comment_count, writer):
            self.title = title
            self.url = url
            self.comment_count = comment_count
            self.writer = writer


    engine = create_engine('sqlite:///habr_blog.db')
    Base.metadata.create_all(engine)

    session_db = sessionmaker(bind=engine)

    session = session_db()

    for soap in get_page(URL):
        posts = get_post_url(soap)
        for url in posts:
            data = get_post_data(url)
            sql_writer = Writer(data['writer']['name'], data['writer']['url'])
            sql_post = Post(data['title'], data['url'], data['comment_count'], sql_writer.id)
            sql_comment_writers = []
            for item in data['comment_writers']:
                sql_comment_writer = Comment_writer(item,
                                                    data['comment_writers'][item], sql_post.id)
                sql_comment_writers.append(sql_comment_writer)
            session.add_all(sql_post)
            session.add(sql_writer)
            session.commit()
            session.add(sql_comment_writer)
            session.commit()

