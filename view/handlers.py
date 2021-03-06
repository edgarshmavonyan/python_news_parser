from abc import abstractmethod
from database.models import *
from database.update_db import update_decorator
from database.tfidf import *
from .graphs import manage_graphs
from collections import Counter
import operator
import json


def make_href(href, text=None):
    """Makes href html-tag
    :param href: str reference
    :param text: text for href"""
    return '<a href="{}">{}</a>'.format(href, href if text is None else text)


class Handler:
    """Handler interface"""
    @classmethod
    @abstractmethod
    def handle(cls, bot, update, args):
        """Main handler method
        :param bot: telegram.Bot
            Bot to work with
        :param update:
            Update to work with
        :param args:
            Arguments to handler"""
        pass

    @classmethod
    @abstractmethod
    def help(cls):
        """Returns help for query
        :return: help string"""
        pass


class StartHandler(Handler):
    """Handles /start query"""
    @classmethod
    def handle(cls, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text='Это бот для сбора статистики, '
                              'наберите /help для ознакомления с командами')


class NewDocsHandler(Handler):
    """Handles /new_docs query"""
    DEFAULT_NEW_DOCS = 5

    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):

        if len(args) > 1:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Наберите не более, чем одно число')
            return
        if len(args) == 1:
            try:
                number = int(args[0])
            except ValueError:
                bot.send_message(chat_id=update.message.chat_id,
                                 text='Ожидалось целое число')
                return
        else:
            number = NewDocsHandler.DEFAULT_NEW_DOCS

        news_db.connect(reuse_if_open=True)

        query = Article.select(Article.section, Article.title,
                               Article.url).\
            order_by(Article.last_update.desc()).limit(number)

        docs = list()

        for article in query:
            docs.append(make_href(article.url,
                                  article.section.name +
                                  ': ' + article.title))

        if len(docs) == 0:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Нет доступных документов',
                             parse_mode='HTML')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='\n'.join(docs),
                             parse_mode='HTML')

    @classmethod
    def help(cls):
        return '/new_docs <N> ; Вывести <N> самых свежих новостей'


class NewTopicsHandler(Handler):
    """Handles /new_topics query"""
    DEFAULT_NEW_TOPICS = 5

    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        # try except
        if len(args) > 1:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Наберите не более, чем одно число')
            return

        if len(args) == 1:
            try:
                number = int(args[0])
            except ValueError:
                bot.send_message(chat_id=update.message.chat_id,
                                 text='Ожидалось целое число')
                return
        else:
            number = NewTopicsHandler.DEFAULT_NEW_TOPICS

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

    @classmethod
    def help(cls):
        return '/new_topics <N> ; Вывести <N> самых свежих тем'


class DocHandler(Handler):
    """Handles /doc query"""
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

    @classmethod
    def help(cls):
        return '/doc <doc_title> ; Вывести содержимое документа с ' \
               'названием <doc_title>'


class TopicHandler(Handler):
    """Handles /topic query"""
    DOC_PREVIEW_NUMBER = 5

    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        topic_name = ' '.join(args)
        news_db.connect(reuse_if_open=True)
        try:
            section = Section.get(name=topic_name)

            recent_news = map(lambda x: make_href(x.url, x.title),
                              section.articles.select(Article.title,
                                                      Article.url).
                              order_by(Article.last_update.desc()).
                              limit(TopicHandler.DOC_PREVIEW_NUMBER))

            message = section.description + '\n' + '\n'.join(recent_news)

            bot.send_message(chat_id=update.message.chat_id,
                             text=message,
                             parse_mode='HTML')

        except Section.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Тема с таким названием не найдена')

    @classmethod
    def help(cls):
        return '/topic <topic_name> ; Вывести описание темы ' \
               '<topic_name> и {} самых свежих новостей оттуда'\
            .format(TopicHandler.DOC_PREVIEW_NUMBER)


class DescribeDocHandler(Handler):
    """Handles """
    DEFAULT_FILENAME = 'graph.png'

    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        doc_title = ' '.join(args)
        news_db.connect(reuse_if_open=True)
        try:
            article = Article.get(title=doc_title)

            bot.send_message(chat_id=update.message.chat_id,
                             text="Длина документа: {}".
                             format(len(str(article.text))))

            manage_graphs(bot, update, DescribeDocHandler.DEFAULT_FILENAME,
                          json.loads(article.length_distribution),
                          json.loads(article.words_distribution))

        except Article.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Документ с таким названием не найден')

    @classmethod
    def help(cls):
        return '/describe_doc <doc_title> ; Вывести длину документа ' \
               '<doc_title>, распределение частот и длин слов в нем'


class DescribeTopicHandler(Handler):
    """Handles /describe topic"""
    DEFAULT_FILENAME = 'graph.png'

    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        topic_name = ' '.join(args)
        news_db.connect(reuse_if_open=True)
        try:
            section = Section.get(name=topic_name)
            document_number = int(section.articles.count())

            if document_number == 0:
                bot.send_message(chat_id=update.message.chat_id,
                                 text='Нету документов в теме')
                return

            bot.send_message(chat_id=update.message.chat_id,
                             text='Количество документов в теме: ' +
                                  str(document_number))

            length_sum = 0
            word_counter = Counter()
            len_counter = Counter()

            for article in section.articles:
                length_sum += len(str(article.text))
                word_counter += json.loads(article.words_distribution)
                len_counter += json.loads(article.length_distribution)

            bot.send_message(chat_id=update.message.chat_id,
                             text='Средняя длина документов: '
                                  + str(length_sum/document_number))

            manage_graphs(bot, update, DescribeTopicHandler.DEFAULT_FILENAME,
                          len_counter, word_counter, True)

        except Section.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Тема с таким названием не найдена')

    @classmethod
    def help(cls):
        return '/describe_topic <topic_name> ; Вывести кол-во документов '\
               'в теме <topic_name>, среднюю длину документов, распределение'\
               ' частот и длин слов в рамках всей темы'


class WordsHandler(Handler):
    """Handles /words query"""
    @classmethod
    @update_decorator
    def handle(cls, bot, update, args):
        topic_name = ' '.join(args)
        try:
            section = Section.get(name=topic_name)

            word_counter = Counter()

            for article in section.articles:
                word_counter += json.loads(article.words_distribution)

            words_dict = Counter(json.loads(section.words_distribution))
            sum_words = Counter()

            for sect in Section.select():
                sum_words += Counter(json.loads(sect.words_distribution))

            words = [(word[0], get_tf(word, section)*get_idf(word, sum_words))
                     for word in words_dict]
            words = sorted(words, key=operator.itemgetter(1))[-5:]

            message = ', '.join(map(operator.itemgetter(0), words)) + '\n'

            bot.send_message(chat_id=update.message.chat_id,
                             text='Самые популярные слова темы: ' + message)

        except Section.DoesNotExist:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Тема с таким названием не найдена')

    @classmethod
    def help(cls):
        return '/words <topic_name> ; Вывести 5 слов, '\
               'лучше всего описывающих тему'


class HelpHandler(Handler):
    """Handles /help query"""
    @classmethod
    def handle(cls, bot, update):
        """Prints help function from all sublcasses of handlers"""
        mapped = map(lambda x: x.help(), list(Handler.__subclasses__()))
        bot.send_message(chat_id=update.message.chat_id,
                         text='\n'.join(filter(None, mapped)))

    @classmethod
    def help(cls):
        return '/help ; Вывести это сообщение'


class UnknownHandler(Handler):
    """Handles unknown queries"""
    @classmethod
    def handle(cls, bot, update, args=None):
        bot.send_message(chat_id=update.message.chat_id,
                         text='Простите, я не понял, что вы имеете в виду')

    @classmethod
    def help(cls):
        return None
