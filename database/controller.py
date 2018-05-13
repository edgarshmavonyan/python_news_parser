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


def add_section_dicts(dicts, to_close=True):
    news_db.connect(reuse_if_open=True)

    with news_db.atomic():
        for instance in dicts:
            add_if_new(instance)

    if to_close:
        news_db.close()


def add_news_dicts(instances, to_close=True):
    news_db.connect(reuse_if_open=True)
    with news_db.atomic():
        for instance in instances:
            tags = instance.pop('tags')
            article = Article.get_or_create(**instance)[0]
            article.tags.add(tags, clear_existing=True)

            article.section.last_update = max(article.last_update, article.section.last_update)
            article.section.save()
    if to_close:
        news_db.close()


def get_or_create_tags(related_tags, to_close=True):
    news_db.connect(reuse_if_open=True)
    tags = [Tag.get_or_create(**x)[0] for x in related_tags]
    if to_close:
        news_db.close()
    return tags
