import requests
import json
import bs4

headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.122 Safari/537.36'}
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
                     'image': '',
                     'tags': [],
                     'writer': {'name': '',
                                'url': ''}
                     }

    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['title'] = soap.select_one('article h1.blogpost-title').text
    template_data['tags'] = {itm.text: f'{BASE_URL}{itm["href"]}' for itm in soap.select('article a.small')}
    template_data['url'] = post_url
    template_data['image'] = soap.find('div').img['src']
    template_data['writer']['name'] = soap.find('div', attrs={'itemprop': 'author'}).text
    template_data['writer']['url'] = f"{BASE_URL}{soap.find('div', attrs={'itemprop': 'author'}).parent['href']}"
    return template_data


if __name__ == '__main__':
    for soap in get_page(URL):
        tags = {}
        posts = get_post_url(soap)
        data = [get_post_data(url) for url in posts]
        for post in data:
            for url, tag in post['tags'].items():
                if not tags.get(tag):
                    tags[tag] = {'posts': []}
                tags[tag]['url'] = url
                tags[tag]['posts'].append(post['url'])
            with open('{name}.json'.format(name=post['url'].replace('https://', '').replace('/', '_')), 'w') as file:
                file.write(json.dumps(post))
    with open('tags.json', 'w') as file:
        file.write(json.dumps(tags))
