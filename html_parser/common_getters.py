from unicodedata import normalize


UNICODE_NORMAL_FORM = 'NFKC'


def get_name_from_tag(tag):
    return normalize(UNICODE_NORMAL_FORM, tag.find('span', class_='item__title').get_text())


def get_url_from_tag(tag):
    return normalize(UNICODE_NORMAL_FORM, tag.find('a').get('href'))
