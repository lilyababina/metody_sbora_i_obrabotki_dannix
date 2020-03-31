# В этом файле объединены три файла - main, models, database
# очень тяжело оказалось разобраться с добавлением записей в бд (не было подробных примеров на вебинаре)-  видимо знаний python не хватает
# все остальное получилось самостоятельно реализовать
#поэтому рассмотрела объяснение домашнего задания и немного дополнила ваш вариант
# database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
#from models_hw3 import Base

class DataBase:

    def __init__(self, url):
        # engine = create_engine('sqlite://gb_blog.db')
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        self.__session_db = sessionmaker(bind=engine)

    def get_session(self) -> Session:
        return self.__session_db()


# models
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
    date = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    comment_count = Column(String, unique = False, nullable=False)
    writer_id = Column(Integer, ForeignKey('user.id'))
    writer = relationship('User', back_populates="post")
    comment = relationship('Comment', back_populates="post")

    def __init__(self, title, url, comment_count, writer, date):
        self.title = title
        self.url = url
        self.comment_count = comment_count
        self.writer = writer
        self.date = date

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer,primary_key=True, autoincrement=True)
    writer_id = Column(Integer, ForeignKey('user.id'))
    writer = relationship('User', back_populates="comment")
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship('Post', back_populates="comment")

    def __init__(self, writer, post):
        self.writer = writer
        self.post = post

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', back_populates="writer")
    comment = relationship('Comment', back_populates="writer")


    def __init__(self, name, url):
        self.name = name
        self.url = url


# main

import requests
import bs4
#from database_hw3 import DataBase
#from models_hw3 import Post, User, Comment

class Parser:
    def __init__(self, start_url):
        self.headers = {'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15'}
        self.__start_url = start_url
        db = DataBase('sqlite:///gb_habr.db')
        self._session = db.get_session()

    def get_soap(self, response):
        return bs4.BeautifulSoup(response.text, 'lxml')

    def get_next(self, soap):
        a = soap.select_one('a#next_page.arrows-pagination__item-link')
        return f'{"https://habr.com"}{a["href"]}' if a else None

    def get_posts_url(self, soap):
        posts = soap.select('div.posts_list ul.content-list li.content-list__item article.post h2 a')
        return [a['href'] for a in posts]

    def get_writer(self, soap):
        url = soap.select_one('a.post__user-info')['href']

        user = self._session.query(User).filter(User.url == url).first()
        if not user:
            soap = self.get_soap(requests.get(url, headers=self.headers))
            user = User(url=url, name= soap.select_one('h1.user-info__name a').text)
            self._session.add(user)
            self._session.commit()
        return user

    def get_writer_comment(self, soap):

        a = soap.find_all('a', attrs={'class': 'user-info user-info_inline'})
        for itm in a:
            url = itm['href']
            user = self._session.query(User).filter(User.url == url).first()
            if not user:
                soap = self.get_soap(requests.get(url, headers=self.headers))
                user = User(url=url, name=soap.select_one('h1.user-info__name a').text)
                self._session.add(user)
                self._session.commit()
            return user

    def parse_post_page(self, url):
        post = self._session.query(Post).filter(Post.url == url).first()
        if post == None:
            response = requests.get(url, headers=self.headers)
            soap = self.get_soap(response)
            
            a = soap.select_one('span.post-stats__comments-count')
            if a == None:
                b = '0'
            else: b = soap.select_one('span.post-stats__comments-count').contents[0]
            data = {
                'title': soap.select_one('span.post__title-text').text,
                'date': soap.select_one('span.post__time')['data-time_published'],
                'writer': self.get_writer(soap),
                'comment_count': b,
                'url': url,
            }

            post = Post(**data)
            self._session.add(post)
            self._session.commit()



    def parse(self):
        url = self.__start_url
        while url:
            resp = requests.get(url, headers=self.headers)
            soap = self.get_soap(resp)
            url = self.get_next(soap)
            url = url if url else None
            for post_url in self.get_posts_url(soap):
                self.parse_post_page(post_url)

            print(1)

if __name__== '__main__':
    start_url = 'https://habr.com/ru/top/weekly/'

    parser = Parser(start_url)
    parser.parse()