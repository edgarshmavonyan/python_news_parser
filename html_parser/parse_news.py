import requests
from bs4 import BeautifulSoup
from .parse_sections import get_name_from_tag, get_url_from_tag, UNICODE_NORMAL_FORM
from .parse_datetime import str_to_datetime
import json
from unicodedata import normalize
from database.models import *
from database.controller import add_news_dict


ITER_SIZE = 200


def get_id_from_section_url(url):
    return url.split('/')[-1]


def get_json_response(section_id, offset=0, limit=ITER_SIZE):
    response = requests.get(
        'https://www.rbc.ru/filter/ajax?story={}&offset={}&limit={}'.format(section_id, offset, limit))
    return json.loads(response.text)


def get_news_tags(json_response):
    html = json_response['html']
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('div', class_='item item_story-single js-story-item')


def get_date_from_tag(tag):
    date_str = normalize(UNICODE_NORMAL_FORM, tag.find('span', class_='item__info').get_text())
    return str_to_datetime(date_str)


def get_news_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def get_news_content(soup):
    article = soup.find('div', class_='article__text')
    for script in article(['script', 'style', 'blockquote', 'div']):
        script.decompose()

    paragraphs = article.find_all('p')
    return normalize(UNICODE_NORMAL_FORM, '\n'.join(filter(None, map(lambda x: x.get_text().strip(), paragraphs))))


def get_tag_info(html_tag):
    return {'name': normalize(UNICODE_NORMAL_FORM, html_tag.get_text())}


def get_related_tags(soup):
    related_tags = soup.find_all('a', class_='article__tags__link')
    return list(map(get_tag_info, related_tags))


def get_news_model_instance(tag, section_url):
    title = get_name_from_tag(tag)
    url = get_url_from_tag(tag)
    soup = get_news_soup(url)
    text = get_news_content(soup)

    ## TO CONTROLLER
    news_db.connect(reuse_if_open=True)
    tags = [Tag.get_or_create(**x)[0] for x in get_related_tags(soup)]
    news_db.close()

    return {'title': title,
            'url': url,
            'section': Section.get(url=section_url),
            'last_update': get_date_from_tag(tag),
            'text': text,
            'tags': tags}


def update_all_news(section_url):
    section_id = get_id_from_section_url(section_url)
    start = 0
    instances = list()
    while True:
        print(start)
        json_response = get_json_response(section_id, start)
        start += ITER_SIZE
        tags = get_news_tags(json_response)
        instances += list(map(lambda tag: get_news_model_instance(tag, section_url), tags))

        if json_response['count'] != ITER_SIZE:
            break

    news_db.connect(reuse_if_open=True)

    with news_db.atomic():
        for instance in instances:
            add_news_dict(instance)

    news_db.close()
