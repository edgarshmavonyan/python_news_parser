from .models import *
import json


def init_db():
    """Initialize database safely"""
    news_db.connect()
    news_db.create_tables([Section,
                           Tag,
                           Article,
                           Article.tags.get_through_model()],
                          safe=True)
    news_db.close()


def add_if_new(instance):
    """Add section if new
    :param instance: dict
        Dict section instance"""
    try:
        Section.get(
            name=instance['name'],
            description=instance['description']
        )
    except Section.DoesNotExist:
        Section.create(**instance, words_distribution=json.dumps(dict()))


def add_section_dicts(dicts, to_close=True):
    """Add list of sections to model
    :param dicts: list
        List of section dicts
    :param to_close: bool
        Whether to close connection (default=False)"""
    news_db.connect(reuse_if_open=True)

    with news_db.atomic():
        for instance in dicts:
            add_if_new(instance)

    if to_close:
        news_db.close()


# def add_words(words, section):

    # print(len(words_section))


def add_news_dicts(instances, to_close=True):
    """Add list of news to model
    :param instances: list
        List of section dicts
    :param to_close: bool
        Whether to close connection (default=False)"""
    news_db.connect(reuse_if_open=True)
    with news_db.atomic():
        for instance in instances:
            tags = instance.pop('tags')
            article, is_new = Article.get_or_create(**instance)
            article.tags.add(tags, clear_existing=True)

            if is_new:
                print('adding')
                words_section = \
                    Counter(json.loads(article.section.words_distribution))
                words = json.loads(article.words_distribution)
                words_section += Counter(words)
                # print(words_section)
                article.section.words_distribution = json.dumps(words_section)

            article.section.last_update = max(article.last_update,
                                              article.section.last_update)
            article.section.save()
    if to_close:
        news_db.close()


def get_or_create_tags(related_tags, to_close=False):
    """Get list of tags or create them
    :param related_tags: list
        List of tags dict instances
    :param to_close: bool
        Whether to close connection (default=False)"""
    news_db.connect(reuse_if_open=True)
    tags = [Tag.get_or_create(**x)[0] for x in related_tags]
    if to_close:
        news_db.close()
    return tags
