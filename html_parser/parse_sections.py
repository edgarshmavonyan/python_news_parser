import requests
from bs4 import BeautifulSoup
import json
from unicodedata import normalize
from database.controller import add_section_dicts
from .decorators import reconnect_decorator


RELEVANT_SECTION_NUMBER = 100
UNICODE_NORMAL_FORM = 'NFKC'


@reconnect_decorator
def get_sections_json(offset=0, limit=RELEVANT_SECTION_NUMBER):
    response = requests.get('https://www.rbc.ru/story/filter/ajax?offset={}&limit={}'.format(offset, limit),
                            allow_redirects=False)
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


def get_section_model_instance(tag):
    return {'name': get_name_from_tag(tag),
            'url': get_url_from_tag(tag),
            'description': get_description_from_tag(tag)
            }


def update_relevant_sections(number=RELEVANT_SECTION_NUMBER):

    if number > RELEVANT_SECTION_NUMBER:
        raise Exception('Too many sections to update (note: maximum is {})'.
                        format(RELEVANT_SECTION_NUMBER))

    json_response = get_sections_json(0, number)
    instances = list(map(get_section_model_instance, get_section_tags(json_response)))
    add_section_dicts(instances)
    return instances
