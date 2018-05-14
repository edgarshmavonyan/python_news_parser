from html_parser.parse_sections import update_relevant_sections, ALL_SECTION_NUMBER
from html_parser.parse_news import update_relevant_section_news
from functools import wraps
from database.models import *
from datetime import datetime, timedelta

UPDATE_TIMEDELTA = timedelta(minutes=10)
UPDATE_SECTION_NUMBER = 15


def update_db(number=ALL_SECTION_NUMBER):
    sections = update_relevant_sections(number)
    news_db.connect(reuse_if_open=True)
    for section in sections:
        update_relevant_section_news(section['url'])
    update_db.last_update = datetime.now()


def update_decorator(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if not hasattr(update_db, 'last_update') or datetime.now() - update_db.last_update > UPDATE_TIMEDELTA:
            update_db(UPDATE_SECTION_NUMBER)

        return func(*args, **kwargs)

    return func_wrapper
