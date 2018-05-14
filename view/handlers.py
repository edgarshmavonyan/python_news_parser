from abc import abstractmethod
from database.models import *
from html_parser.update_db import update_decorator
from .graphs import save_length_ditribution, save_words_distribution, send_graph
import os


def make_href(href, text):
    return '<a href="{}">{}</a>'.format(href, text)


class Handler:
    @classmethod
    @abstractmethod
    def handle(cls, bot, update, args):
        pass


class NewDocsHandler(Handler):
    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):

        if len(args) != 1:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Type exactly one number')
            return

        try:
            number = int(args[0])
        except ValueError:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Type integer, please')
            return

        news_db.connect(reuse_if_open=True)

        query = Article.select(Article.section, Article.title, Article.url).\
            order_by(Article.last_update.desc()).limit(number)

        docs = list()

        for article in query:
            docs.append(make_href(article.url,
                                  article.section.name + ': ' + article.title))

        if len(docs) == 0:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Нет доступных документов',
                             parse_mode='HTML')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='\n'.join(docs),
                             parse_mode='HTML')


class NewTopicsHandler(Handler):
    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        # try except
        if len(args) != 1:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Type exactly one number')
            return

        try:
            number = int(args[0])
        except ValueError:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Type integer, please')
            return

        news_db.connect(reuse_if_open=True)

        query = Section.select(Section.name, Section.url).\
            order_by(Section.last_update.desc()).limit(number)

        sections = list()

        for section in query:
            sections.append(make_href(section.url, section.name))

        if len(sections) == 0:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Нет доступных тем')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='\n'.join(sections),
                             parse_mode='HTML')


class DocHandler(Handler):
    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        doc_title = ' '.join(args)
        news_db.connect(reuse_if_open=True)
        try:
            article = Article.get(title=doc_title)
            bot.send_message(chat_id=update.message.chat_id,
                             text=article.text)

        except Article.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Документ с таким названием не найден')


class TopicHandler(Handler):
    DOC_PREVIEW_NUMBER = 5

    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        topic_name = ' '.join(args)
        news_db.connect(reuse_if_open=True)
        try:
            section = Section.get(name=topic_name)

            recent_news = map(lambda x: make_href(x.url, x.title),
                              section.articles.select(Article.title, Article.url).
                              order_by(Article.last_update.desc()).
                              limit(TopicHandler.DOC_PREVIEW_NUMBER))

            message = section.description + '\n' + '\n'.join(recent_news)

            bot.send_message(chat_id=update.message.chat_id,
                             text=message,
                             parse_mode='HTML')

        except Section.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Тема с таким названием не найдена')


class DescribeDocHandler(Handler):
    DEFAULT_FILENAME = 'graph.png'

    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        doc_title = ' '.join(args)
        news_db.connect(reuse_if_open=True)
        try:
            article = Article.get(title=doc_title)

            bot.send_message(chat_id=update.message.chat_id,
                             text="Длина документа: {}".format(len(str(article.text))))

            save_length_ditribution(article.length_distribution, DescribeDocHandler.DEFAULT_FILENAME)
            send_graph(bot, update, DescribeDocHandler.DEFAULT_FILENAME)

            os.remove(DescribeDocHandler.DEFAULT_FILENAME)

            save_words_distribution(article.words_distribution, DescribeDocHandler.DEFAULT_FILENAME)
            send_graph(bot, update, DescribeDocHandler.DEFAULT_FILENAME)

        except Article.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Документ с таким названием не найден')
