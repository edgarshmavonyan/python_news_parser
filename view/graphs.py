import matplotlib.pyplot as plt
import operator


def save_length_ditribution(distribution, filename):
    distribution = dict(sorted(list(map(lambda x: (int(x[0]), x[1]), distribution.items()))))
    plt.plot(distribution.keys(), distribution.values(), color='green')
    plt.ylabel('Количество слов данной длины')
    plt.xlabel('Длина слова')
    plt.savefig(filename)


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


def send_graph(bot, update, filename):
    with open(filename, 'rb') as photo:
        bot.send_photo(chat_id=update.message.chat_id, photo=photo)
