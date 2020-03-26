import requests
import json
import bs4

headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.122 Safari/537.36'}
URL = 'https://habr.com/ru/top/weekly'
BASE_URL = 'https://habr.com'


def get_post_url(soap: bs4.BeautifulSoup) -> set:
    post_a = soap.select('a.post__title_link')
    return set(f'{a["href"]}' for a in post_a)


def get_next_page(soap: bs4.BeautifulSoup) -> str:
    a = soap.find('a', attrs={'id': 'next_page'})
    # a = div.find("a")
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
                     'coment_count': '',
                     'public_time': '',
                     'writer': {'name': '',
                                'url': ''},
                     'comment_writers': [{'name': 'url'}]
                     }

    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['title'] = soap.select_one('div.post__wrapper h1 span').text
    template_data['url'] = post_url
    template_data['coment_count'] = soap.select_one('span.comments-section__head-counter',
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
    for soap in get_page(URL):
        posts = get_post_url(soap)
        data = [get_post_data(url) for url in posts]
        for post in data:
            with open('{name}.json'.format(name=post['title'].replace('/', '_')), 'w') as file:
                file.write(json.dumps(post))

    print(1)
