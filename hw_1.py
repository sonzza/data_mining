import requests
import json
import time

URL = 'https://5ka.ru/api/v2/special_offers/'
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.122 Safari/537.36'}
CAT_URL = 'https://5ka.ru/api/v2/categories/'

categories_for_pages = requests.get(CAT_URL, headers=headers)
cata_dict = categories_for_pages.json()
cata_for_pages = []
cata_for_groups = []
for i in range(len(cata_dict)):
    cata_for_pages.append(cata_dict[i]['parent_group_code'])
    cata_for_groups.append(cata_dict[i]['parent_group_name'])


def x5ka(url, params):
    result = []
    while url:
        response = requests.get(url, headers=headers, params=params) if params else requests.get(url, headers=headers)
        params = None
        data = response.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(3)
    return result


if __name__ == '__main__':
    for i in range(len(cata_for_pages)):
        data = x5ka(URL, {'categories': cata_for_pages[i]})
        with open('{name}.json'.format(name=cata_for_groups[i]), 'w') as file:
            file.write(json.dumps(data))
