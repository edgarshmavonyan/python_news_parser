from controller.queries import *
from telegram.ext import CommandHandler, Updater


def main():
    updater = Updater(token='585285364:AAFBx3Kotx7txqpBN03RXYHHm_e1ViGqNjY',
                      request_kwargs={'proxy_url': 'socks5://138.68.98.172:1080/'}
                      )
    dispatcher = updater.dispatcher
    import logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    new_docs_handler = CommandHandler('new_docs', NewDocsHandler.handle, pass_args=True)
    dispatcher.add_handler(new_docs_handler)

    new_topics_handler = CommandHandler('new_topics', NewTopicsHandler.handle, pass_args=True)
    dispatcher.add_handler(new_topics_handler)

    topic_handler = CommandHandler('topic', TopicHandler.handle, pass_args=True)
    dispatcher.add_handler(topic_handler)

    doc_handler = CommandHandler('doc', DocHandler.handle, pass_args=True)
    dispatcher.add_handler(doc_handler)

    updater.start_polling()

    while True:
        wait_input = input()
        if wait_input == 'stop':
            updater.stop()
            return 'Stopped'


if __name__ == '__main__':
    main()
