from copy import deepcopy
import scrapy
import re
import json
from urllib.parse import urljoin, urlencode


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    graphql_url = 'https://www.instagram.com/graphql/query/?'

    start_urls = ['https://www.instagram.com/']
    parse_users = ['ben_the_rough_collie', 'honzahruban']
    variables = {"id": '',
                 "include_reel": True,
                 "fetch_mutual": False,
                 "first": 100,
                 }


    def __init__(self, logpass: tuple, **kwargs):
        self.login, self.pwd = logpass
        #self.query_hash = 'c76146de99bb02f6415203be841dd25a' #подписчики
        self.query_hash_following = 'd04b0a864b4b54837c0d870b0e77e076'#подписки
        super().__init__(**kwargs)

    def parse(self, response):
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            login_url,
            method='POST',
            callback=self.main_parse,
            formdata={'username': self.login, 'password': self.pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def main_parse(self, response):
        j_resp = json.loads(response.text)
        if j_resp.get('authenticated'):# проверили прошли ли аутэнтификацию или нет
            for u_name in self.parse_users:
                yield response.follow(
                    urljoin(self.start_urls[0], u_name),
                    callback=self.parse_user,
                    cb_kwargs={'user_name': u_name}
                )

    def parse_user(self, response, user_name: str):
        user_id = self.fetch_user_id(response.text, user_name)
        user_vars = deepcopy(self.variables)
        user_vars.update({'id': user_id})

        url = self.make_grapthql_url(user_vars, self.query_hash_following) #для following
        #url = self.make_grapthql_url(user_vars, self.query_hash) #для followers
        yield response.follow(
            url,
            callback=self.parse_following,
            cb_kwargs={'user_vars': user_vars, 'user_name': user_name, }
        )

    def parse_following(self, response, user_vars, user_name):
        j_response = json.loads(response.text)
        #сделать обработчик try except
        if j_response['data']['user']['edge_follow']['page_info']['has_next_page']:
            user_vars.update({'after': j_response['data']['user']['edge_follow']['page_info']['end_cursor']})
            url = self.make_grapthql_url(user_vars, self.query_hash_following)
            yield response.follow(
                url,
                callback=self.parse_following,
                cb_kwargs={'user_vars': user_vars, 'user_name': user_name}
            )

        followings = j_response['data']['user']['edge_follow']['edges']

        for following in followings:
            yield {'user_name': user_name, 'user_id': user_vars['id'], 'following': following['node']}

    def fetch_csrf_token(self, text):
        """Используя регулярные выражения парсит переданную строку на наличие
        `csrf_token` и возвращет его."""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        `id` нужного пользователя и возвращет его."""
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def make_grapthql_url(self, user_vars, query_hash):
        return f'{self.graphql_url}query_hash={query_hash}&{urlencode(user_vars)}'

class InstagramSpider_2(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    start_urls = ['https://instagram.com/']
    parse_users = ['ben_the_rough_collie', 'honzahruban' ]
    variables = {"id": '',
                 "include_reel": True,
                 "fetch_mutual": False,
                 "first": 100,
                 }
    def __init__(self, logpass: tuple, **kwargs):
        self.login, self.pwd = logpass
        self.query_hash = 'c76146de99bb02f6415203be841dd25a' #подписчики
        #self.query_hash_following = 'd04b0a864b4b54837c0d870b0e77e076'#подписки
        super().__init__(**kwargs)

    def parse(self, response):
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            login_url,
            method='POST',
            callback=self.main_parse,
            formdata={'username': self.login, 'password': self.pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def main_parse(self, response):
        j_resp = json.loads(response.text)
        if j_resp.get('authenticated'):
            for u_name in self.parse_users:
                yield response.follow(
                    urljoin(self.start_urls[0], u_name),
                    callback=self.parse_user,
                    cb_kwargs={'user_name': u_name}
                )

    def parse_user(self, response, user_name: str):
        user_id = self.fetch_user_id(response.text, user_name)
        user_vars = deepcopy(self.variables)
        user_vars.update({'id': user_id})
        url = self.make_grapthql_url(user_vars, self.query_hash)
        yield response.follow(
            url,
            callback=self.parse_followers,
            cb_kwargs={'user_vars': user_vars, 'user_name': user_name, }
        )

    def parse_followers(self, response, user_vars, user_name):
        j_response = json.loads(response.text)
        #сделать обработчик try except
        if j_response['data']['user']['edge_followed_by']['page_info']['has_next_page']:
            user_vars.update({'after': j_response['data']['user']['edge_followed_by']['page_info']['end_cursor']})
            url = self.make_grapthql_url(user_vars, self.query_hash)
            yield response.follow(
                url,
                callback=self.parse_followers,
                cb_kwargs={'user_vars': user_vars, 'user_name': user_name}
            )

        followers = j_response['data']['user']['edge_followed_by']['edges']

        for follower in followers:
            yield {'user_name': user_name, 'user_id': user_vars['id'], 'follower': follower['node']}
        print(1)


    def fetch_csrf_token(self, text):

        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):

        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def make_grapthql_url(self, user_vars, query_hash):
        return f'{self.graphql_url}query_hash={query_hash}&{urlencode(user_vars)}'