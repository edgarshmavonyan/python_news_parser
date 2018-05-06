from .models import *


def init_db():
    news_db.connect()
    news_db.create_tables([Section, Tag, Article, Article.tags.get_through_model()])
    news_db.close()


def add_if_new(instance):
    try:
        Section.get(
            name=instance['name'],
            description=instance['description']
        )
    except Section.DoesNotExist:
        Section.create(**instance)


def add_section_dicts(dicts):
    news_db.connect(reuse_if_open=True)

    with news_db.atomic():
        for instance in dicts:
            add_if_new(instance)

    news_db.close()


def add_news_dict(instance, to_open=False):
    if to_open:
        news_db.connect(reuse_if_open=True)
    tags = instance.pop('tags')
    article = Article.get_or_create(**instance)[0]

    article.tags.add(tags, clear_existing=True)
    if to_open:
        news_db.close()
