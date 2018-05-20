import view.handlers as hnd
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
from database.update_db import update_db, UPDATE_SECTION_NUMBER
from database.controller import init_db
from database.models import news_db
import logging


def create_handlers(updater):
    dispatcher = updater.dispatcher
    handlers = list()
    handlers.append(CommandHandler('start',
                                   hnd.StartHandler.handle))
    handlers.append(CommandHandler('new_docs',
                                   hnd.NewDocsHandler.handle,
                                   pass_args=True))
    handlers.append(CommandHandler('new_topics',
                                   hnd.NewTopicsHandler.handle,
                                   pass_args=True))
    handlers.append(CommandHandler('topic',
                                   hnd.TopicHandler.handle,
                                   pass_args=True))
    handlers.append(CommandHandler('doc',
                                   hnd.DocHandler.handle,
                                   pass_args=True))
    handlers.append(CommandHandler('describe_doc',
                                   hnd.DescribeDocHandler.handle,
                                   pass_args=True))
    handlers.append(CommandHandler('describe_topic',
                                   hnd.DescribeTopicHandler.handle,
                                   pass_args=True))
    handlers.append(CommandHandler('words',
                                   hnd.WordsHandler.handle,
                                   pass_args=True))
    handlers.append(CommandHandler('help',
                                   hnd.HelpHandler.handle,
                                   pass_args=False))
    handlers.append(MessageHandler(Filters.command,
                                   hnd.UnknownHandler.handle))
    handlers.append(MessageHandler(Filters.text,
                                   hnd.UnknownHandler.handle))

    [dispatcher.add_handler(handler) for handler in handlers]


# request_kwargs={'proxy_url': 'socks5://138.68.98.172:1080/'}
def main():
    init_db()
    update_db()

    updater = Updater(token='585285364:AAFBx3Kotx7txqpBN03RXYHHm_e1ViGqNjY')

    logging.basicConfig(format='%(asctime)s - %(name)s - '
                               '%(levelname)s - %(message)s',
                        level=logging.INFO)

    create_handlers(updater)

    updater.start_polling()

    print('Started polling')
    print('Type "stop" to stop bot')

    while True:
        wait_input = input()
        if wait_input == 'stop':
            updater.stop()
            news_db.close()
            print('Stopped')
            return


if __name__ == '__main__':
    main()
