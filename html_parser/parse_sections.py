import requests
from bs4 import BeautifulSoup
import json
from unicodedata import normalize
from database.controller import add_section_dicts

ITER_SIZE = 100
UNICODE_NORMAL_FORM = 'NFC'
# THEME_CSS_CLASS = 'item item_story js-story-item'


def get_json_response(offset=0, limit=ITER_SIZE):
    response = requests.get('https://www.rbc.ru/story/filter/ajax?offset={}&limit={}'.format(offset, limit))
    return json.loads(response.text)


def get_section_tags(json_response):
    html = json_response['html']
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('div', class_='item item_story js-story-item')


def get_name_from_tag(tag):
    return normalize(UNICODE_NORMAL_FORM, tag.find('span', class_='item__title').get_text())


def get_url_from_tag(tag):
    return normalize(UNICODE_NORMAL_FORM, tag.find('a').get('href'))


def get_description_from_tag(tag):
    return normalize(UNICODE_NORMAL_FORM, tag.find('span', class_='item__text').get_text().strip())


def get_dict_model_instance(tag):
    return {'name': get_name_from_tag(tag),
            'url': get_url_from_tag(tag),
            'description': get_description_from_tag(tag)
            }


from itertools import chain
from time import time


def get_all_and_store(iter_size=ITER_SIZE):
    start = 0
    instances = list()
    timer = time()
    while True:
        json_response = get_json_response(start, iter_size)
        start += iter_size
        # instances = chain(instances, map(get_dict_model_instance, get_section_tags(json_response)))
        instances += list(map(get_dict_model_instance, get_section_tags(json_response)))
        if json_response['count'] != iter_size:
            break
    print(time() - timer)
    timer = time()
    add_section_dicts(instances)
    print(time() - timer)

