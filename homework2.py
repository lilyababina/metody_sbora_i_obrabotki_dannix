import requests
from bs4 import BeautifulSoup
import json



def get_urls(url, short_url):
    list_post_url = []
    start_url = url
    while url:
        response = requests.get(url)
        soap = BeautifulSoup(response.text, 'lxml')
        li = soap.find('ul', attrs={'class': 'gb__pagination'}).find_all('li', attrs={'class': 'page'})
        div = soap.find('div', attrs={'class': 'post-items-wrapper'}).find_all('div', attrs={'class': 'post-item event'})
        for i in range(len(div)):
            list_post_url.append(short_url + div[i].find('a').attrs['href'])

        if li[-1].find('a').attrs['href'] == li[0].find('a').attrs['href'] and url != start_url:
            url = None
        else:
            url = short_url + li[-1].find('a').attrs['href']

    return list_post_url

def get_urls_tags(url, short_url):
    list_post_url = []
    start_url = url
    while url:
        response = requests.get(url)
        soap = BeautifulSoup(response.text, 'lxml')
        if soap.find('ul', attrs={'class': 'gb__pagination'}) == None:
            div = soap.find('div', attrs={'class': 'post-items-wrapper'}).find_all('div', attrs={'class': 'post-item event'})
            for i in range(len(div)):
                list_post_url.append(short_url + div[i].find('a').attrs['href'])
            url = None

        else:
            li = soap.find('ul', attrs={'class': 'gb__pagination'}).find_all('li', attrs={'class': 'page'})
            div = soap.find('div', attrs={'class': 'post-items-wrapper'}).find_all('div', attrs={'class': 'post-item event'})
            for i in range(len(div)):
                list_post_url.append(short_url + div[i].find('a').attrs['href'])

            if li[-1].find('a').attrs['href'] == li[0].find('a').attrs['href'] and url != start_url:
                url = None
            else:
                url = short_url + li[-1].find('a').attrs['href']

    return list_post_url

# todo пройти ленту блога для получения полных url всех постов
url = 'https://geekbrains.ru/posts'
short_url = 'https://geekbrains.ru'

list_post_url = get_urls(url, short_url)


# todo зайти на страницу с постом
tag_name_url = []  # необработанная информация с tag и их url списком

for i in range(len(list_post_url)):
    response = requests.get(list_post_url[i])
    soap = BeautifulSoup(response.text, 'lxml')
    data_class_small = soap.find_all('a', attrs={'class': 'small'})
    tag_name_url.append(data_class_small)

#todo получить информацию для записи в блоге

for i in range(10):  # вообще цикл нужно сделать для каждого поста, то есть до len(list_post_url), но для экономии времени и ресурсов делаю на примере 10
    response = requests.get(list_post_url[i])
    soap = BeautifulSoup(response.text, 'lxml')

    image_url = soap.find('div', attrs={'class': 'blogpost-content content_text content js-mediator-article'}).find_all('p')[0].find('img').attrs['src']
    title = soap.find('article', attrs={'class': 'col-sm-6 col-md-8 blogpost__article-wrapper'}).find('h1', attrs={'class': 'blogpost-title text-left text-dark m-t-sm'}).text
    full_writer_url = 'https://geekbrains.ru' + soap.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'}).find('a').attrs['href']
    writer_name = soap.find('div', attrs={'class': 'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'}).find('div', attrs={'class': 'text-lg text-dark'}).text

    tags_for_json = []
    for j in range(len(soap.find_all('a', attrs={'class': 'small'}))):
        tags_for_json.append({soap.find_all('a', attrs={'class': 'small'})[j].text: ('https://geekbrains.ru' + soap.find_all('a', attrs={'class': 'small'})[j].attrs['href'])})

    # формируем данные для json файла
    data_for_posts_json = []
    data_for_posts_json.append({'url' : list_post_url[i], 'image' : image_url, 'writer' : {'name': writer_name, 'url': full_writer_url}, 'tags': tags_for_json })
    # сохраняем файл
    with open(list_post_url[i][28:] + '.json', "w") as write_file:
        json.dump(data_for_posts_json, write_file)





# todo обработать tag_name_url для получения списка имен и списка url tag
tag_url = []
tag_name = []
for i in range(len(tag_name_url)):
    for j in range(len(tag_name_url[i])):
        if tag_name_url[i][j].contents[0] not in tag_name:
            tag_name.append(tag_name_url[i][j].contents[0])
            tag_url.append(short_url + tag_name_url[i][j].attrs['href'])


# todo создать данные для файла tags.json
data_for_tags_json=[]
for i in range(len(tag_url)):
    data_for_tags_json.append({tag_name[i]: {"url": tag_url[i],"posts": []}})

# todo пройтись по url tags для того что бы получить url постов для каждого tag
for i in range(len(tag_url)):
    url=tag_url[i]
    shot_url='https://geekbrains.ru'
    list_post_url_for_tag = get_urls_tags(url, short_url)
    for j in range(len(list_post_url_for_tag)):
        data_for_tags_json[i][tag_name[i]]['posts'].append(list_post_url_for_tag[j])

with open("tags.json", "w") as write_file:
    json.dump(data_for_tags_json, write_file)







