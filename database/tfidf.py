from database.models import *
from collections import Counter
import json


INF = 100000


def get_idf(word, sum_words=None):
    if sum_words is None:
        sum_words = Counter()
        for section in Section.select():
            sum_words += Counter(json.loads(section.words_distribution))
    denom = sum(map(lambda x: 1 if word in x else 0, sum_words))
    if denom == 0:
        return INF
    else:
        return len(list(Section.select())) / denom


def get_sum_occur(word):
    result = 0
    for section in Section.select():
        result += Counter(json.loads(section.words_distribution))[word]
    return result


def get_tf(word, section):
    return Counter(json.loads(section.words_distribution))[word] / get_sum_occur(word)
