# import matplotlib
# matplotlib.use("Agg")
# import matplotlib.pyplot as plt
import operator
import os

plt = dict()
def save_length_distribution(distribution, filename):
    distribution = dict(sorted(list(map(lambda x: (int(x[0]), x[1]), distribution.items()))))
    plt.plot(distribution.keys(), distribution.values(), color='green')
    plt.ylabel('Количество слов данной длины')
    plt.xlabel('Длина слова')
    plt.savefig(filename)
    plt.clf()


def save_words_distribution(distribution, filename, logarithmic=False):
    distribution = (sorted(distribution.items(), key=operator.itemgetter(1)))[::-1]
    ylabel = list(map(operator.itemgetter(1), distribution))
    if logarithmic:
        plt.loglog(range(len(ylabel)), ylabel)
    else:
        plt.plot(ylabel)
    plt.ylabel('Количество появлений слова')
    plt.xlabel('Слова')
    plt.savefig(filename)
    plt.clf()


def send_graph(bot, update, filename):
    with open(filename, 'rb') as photo:
        bot.send_photo(chat_id=update.message.chat_id, photo=photo)


def manage_graphs(bot, update, filename,
                  length_distribution, words_distribution, logarithmic=False):

    save_length_distribution(length_distribution, filename)

    send_graph(bot, update, filename)

    os.remove(filename)

    save_words_distribution(words_distribution, filename, logarithmic)

    send_graph(bot, update, filename)

    os.remove(filename)
