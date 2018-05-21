from bs4 import BeautifulSoup
from unicodedata import normalize
from database.controller import add_section_dicts
from .reconnect import reconnect_decorator
from .common_getters import get_name_from_tag, get_url_from_tag
from .common_getters import UNICODE_NORMAL_FORM
import json
import requests

ALL_SECTION_NUMBER = 10


@reconnect_decorator
def get_sections_json(offset=0, limit=ALL_SECTION_NUMBER):
    """Gets json list of sections from rbc
    :param offset: int
        Number of latest sections to ignore
    :param limit: int
        Number of sections to download (note: max is 200)
    :return: dict response with sections"""
    response = requests.\
        get('https://www.rbc.ru/story/filter/ajax?offset={}&limit={}'.
            format(offset, limit), allow_redirects=False)
    return json.loads(response.text)


def get_section_tags(json_response):
    """Get html-tags containing sections
    :param json_response: dict
        Json response of the server
    :return: list of html-tags"""
    html = json_response['html']
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('div', class_='item item_story js-story-item')


def get_description_from_tag(tag):
    """Get section description from html-tag
    :param tag: bs4.Tag
        Html-tag of section
    :return: string description"""
    return normalize(UNICODE_NORMAL_FORM,
                     tag.find('span', class_='item__text').get_text().strip())


def get_section_model_instance(tag):
    """Get json instance for writing to database
    :param tag: bs4.Tag
        Html-tag of section
    :return: dict section"""
    return {'name': get_name_from_tag(tag),
            'url': get_url_from_tag(tag),
            'description': get_description_from_tag(tag)
            }


def update_relevant_sections(number):
    """Update number of sections
    :param number: int
        Number of sections to update
    :return: list of dict model instances"""
    if number > ALL_SECTION_NUMBER:
        raise Exception('Too many sections to update (note: maximum is {})'.
                        format(ALL_SECTION_NUMBER))

    json_response = get_sections_json(0, number)
    instances = list(map(get_section_model_instance,
                         get_section_tags(json_response)))
    add_section_dicts(instances)
    return instances
