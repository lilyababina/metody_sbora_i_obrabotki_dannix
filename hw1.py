import requests
import json
import time

CAT_URL = 'https://5ka.ru/api/v2/categories/'
URL = 'https://5ka.ru/api/v2/special_offers/'
headers = {'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15'}

def x5ka(url, params=dict()):
    result = []
    while url:
        response = requests.get(url, headers=headers, params=params) if params else requests.get(url, headers=headers)
        params = None
        data = response.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(1)
    return result

if __name__ == '__main__':
# выгрузили категории
    response = requests.get(CAT_URL, headers=headers)
    categories_data = response.json()

# для каждой категории выгрузить товары и сохранить в файл

    for i in range(len(categories_data)):
        data = x5ka(URL, {'categories': categories_data[i].get('parent_group_code')})
        nameFile = categories_data[i].get('parent_group_name')
        with open(nameFile + '.json', 'w') as file:
            file.write(json.dumps(data))

