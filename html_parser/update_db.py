from .parse_sections import update_relevant_sections
from .parse_news import update_relevant_section_news
from database.models import *


def update_db():
    sections = update_relevant_sections()
    news_db.connect(reuse_if_open=True)
    for section in sections:
        print(section['name'])
        update_relevant_section_news(section['url'])
