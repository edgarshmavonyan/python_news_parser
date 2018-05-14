from bs4 import BeautifulSoup
from .common_getters import get_name_from_tag, get_url_from_tag, UNICODE_NORMAL_FORM
from .parse_datetime import str_to_datetime
from .reconnect import reconnect_decorator
from unicodedata import normalize
from database.models import *
from database.controller import add_news_dicts, get_or_create_tags
from collections import Counter
import re
import json
import requests


RELEVANT_NEWS_NUMBER = 100


def get_id_from_section_url(url):
    return url.split('/')[-1]


@reconnect_decorator
def get_news_json(section_id, offset=0, limit=RELEVANT_NEWS_NUMBER):
    response = requests.get(
        'https://www.rbc.ru/filter/ajax?story={}&offset={}&limit={}'.format(section_id, offset, limit),
        allow_redirects=False)
    return json.loads(response.text)


def get_news_tags(json_response):
    html = json_response['html']
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('div', class_='item item_story-single js-story-item')


def get_date_from_tag(tag):
    date_str = normalize(UNICODE_NORMAL_FORM, tag.find('span', class_='item__info').get_text())
    return str_to_datetime(date_str)


@reconnect_decorator
def get_news_soup(url):
    response = requests.get(url, allow_redirects=False)
    return BeautifulSoup(response.text, 'html.parser')


def get_news_content(soup):
    article = soup.find('div', class_='article__text')
    if article is None:
        return None
    for script in article(['script', 'style', 'blockquote', 'div']):
        script.decompose()

    paragraphs = article.find_all('p')
    return normalize(UNICODE_NORMAL_FORM, '\n'.join(filter(None, map(lambda x: x.get_text().strip(),paragraphs))))


def get_tag_info(html_tag):
    return {'name': normalize(UNICODE_NORMAL_FORM, html_tag.get_text())}


def get_related_tags(soup):
    related_tags = soup.find_all('a', class_='article__tags__link')
    return list(map(get_tag_info, related_tags))


def filter_text(text):
    return list(filter(None, re.split('\W+|[0-9]+', text.lower())))


def get_length_distribution(text, filtered=True):
    if not filtered:
        text = filter_text(text)
    return dict(Counter(map(len, text)))


def get_words_distribution(text, filtered=True):
    if not filtered:
        text = filter_text(text)
    return dict(Counter(text))


def get_news_model_instance(tag, section_url):
    title = get_name_from_tag(tag)
    url = get_url_from_tag(tag)
    date = get_date_from_tag(tag)

    try:
        Article.get(title=title, url=url, last_update=date)
    except Article.DoesNotExist:
        pass
    else:
        return None

    soup = get_news_soup(url)
    text = get_news_content(soup)

    if text is None:
        return None

    filtered_text = filter_text(text)
    words_distribution = get_words_distribution(filtered_text)
    length_distribution = get_length_distribution(filtered_text)
    tags = get_or_create_tags(get_related_tags(soup))

    return {'title': title,
            'url': url,
            'section': Section.get(url=section_url),
            'last_update': date,
            'text': text,
            'tags': tags,
            'length_distribution': json.dumps(length_distribution),
            'words_distribution': json.dumps(words_distribution)
            }


def update_relevant_section_news(section_url, number=RELEVANT_NEWS_NUMBER):
    if number > RELEVANT_NEWS_NUMBER:
        raise Exception('Too many news to update (note: maximum is {})'
                        .format(RELEVANT_NEWS_NUMBER))

    section_id = get_id_from_section_url(section_url)

    json_response = get_news_json(section_id, 0, number)
    tags = get_news_tags(json_response)

    instances = list(filter(None, map(lambda tag: get_news_model_instance(tag, section_url), tags)))
    add_news_dicts(instances)
