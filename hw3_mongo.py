import requests
import json
import bs4
from pymongo import MongoClient

headers = {'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15'}
URL = 'https://habr.com/ru/top/weekly/'
BASE_URL = 'https://habr.com'


def get_next_page(soap: bs4.BeautifulSoup) -> str:
    a = soap.find('div', attrs = {'class': 'page__footer'}).find('a', attrs = {'class': 'arrows-pagination__item-link arrows-pagination__item-link_next'})
    return f'{BASE_URL}{a["href"]}' if a else None

def get_post_url(soap: bs4.BeautifulSoup) -> list:
    post_a = soap.find_all('a', attrs = {'class': 'post__title_link'})
    return list(f'{a["href"]}' for a in post_a)

def get_page(url):
    while url:
        print(url)
        response = requests.get(url, headers=headers)
        soap = bs4.BeautifulSoup(response.text, 'lxml')
        yield soap
        url = get_next_page(soap)

def get_post_data(post_url:str) -> dict:
    template_data = {'url': '',
                     'title': '',
                     'comments_count': '',
                     'date_post': '',
                     'time_post': '',
                     'writer': {'name': '',
                                'url': ''},
                     'name_comments': [],
                     }
    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['url'] = post_url
    template_data['title'] = soap.select_one('span.post__title-text').text
    if soap.select_one('span.post-stats__comments-count') is None:
        template_data['comments_count'] = 0
    else: template_data['comments_count'] = int(soap.select_one('span.post-stats__comments-count').text)
    template_data['date_post'] = soap.select_one('span.post__time').text[:13]
    template_data['time_post'] = soap.select_one('span.post__time').text[16:]
    template_data['writer']['url'] = soap.find('a', attrs={'class': 'post__user-info user-info'})['href']
    template_data['writer']['name'] = soap.find('a', attrs={'class': 'post__user-info user-info'})['href']
    a = soap.find_all('span', attrs={'class': 'user-info__nickname user-info__nickname_small user-info__nickname_comment'})
    for itm in a:
        if itm.text not in template_data['name_comments']:
            template_data['name_comments'].append(itm.text)

    return template_data



if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client['db_blog']

    posts = []
    url = URL
    while url:
        print(url)
        response = requests.get(url, headers=headers)
        soap = bs4.BeautifulSoup(response.text, 'lxml')
        posts = posts + get_post_url(soap)
        url = get_next_page(soap)

    data = [get_post_data(itm) for itm in posts]
    db['habr_posts'].insert_many(data)



