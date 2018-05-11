from abc import abstractmethod
from database.models import *


def make_href(href, text):
    return '<a href="{}">{}</a>'.format(href, text)


class Handler:
    @classmethod
    @abstractmethod
    def handle(cls, bot, update, args):
        pass


class NewDocsHandler(Handler):
    @classmethod
    def handle(cls, bot, update, args):
        # updater
        number = int(args[0])
        news_db.connect()

        query = Article.select(Article.section, Article.title, Article.url).\
            order_by(Article.last_update.desc()).limit(number)

        docs = list()

        for article in query:
            docs.append(make_href(article.url,
                                  article.section.name + ': ' + article.title))

        news_db.close()

        if len(docs) == 0:
            bot.send_message(chat_id=update.message.chat_id
                             , text='Нет доступных документов'
                             , parse_mode='HTML')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='\n'.join(docs),
                             parse_mode='HTML')


class NewTopicsHandler(Handler):
    @classmethod
    def handle(cls, bot, update, args):
        # updater
        # try except
        number = int(args[0])

        news_db.connect()

        query = Section.select(Section.name, Section.url).\
            order_by(Section.last_update.desc()).limit(number)

        sections = list()

        for section in query:
            sections.append(make_href(section.url, section.name))

        news_db.close()

        if len(sections) == 0:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Нет доступных тем')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='\n'.join(sections),
                             parse_mode='HTML')


class DocHandler(Handler):
    @classmethod
    def handle(cls, bot, update, args):
        doc_title = args[0]
        try:
            article = Article.select(Article.text, Article.title).get(title=doc_title)
            bot.send_message(chat_id=update.message.chat_id,
                             text=article.text)

        except Article.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Документ с таким названием не найден')


class TopicHandler(Handler):
    DOC_PREVIEW_NUMBER = 5

    @classmethod
    def handle(cls, bot, update, args):
        topic_name = ' '.join(args)
        try:
            section = Section.select(Section.name,
                                     Section.description).get(name=topic_name)

            recent_news = map(lambda x: make_href(x.url, x.title),
                              Article.select(Article.title, Article.url).
                              where(Article.section == section).
                              limit(TopicHandler.DOC_PREVIEW_NUMBER))

            message = section.description + '\n' + '\n'.join(recent_news)

            bot.send_message(chat_id=update.message.chat_id,
                             text=message)

        except Section.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Тема с таким названием не найдена')