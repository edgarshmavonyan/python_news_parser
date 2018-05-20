from unicodedata import normalize


UNICODE_NORMAL_FORM = 'NFKC'


def get_name_from_tag(tag):
    """Gets title of news or section from html-tag
    :param tag: bs4.Tag
        Html-tag of object
    :return: string name"""
    return normalize(UNICODE_NORMAL_FORM,
                     tag.find('span', class_='item__title').get_text())


def get_url_from_tag(tag):
    """Gets url of news or section from html-tag
    :param tag: bs4.Tag
        Html-tag of object
    :return: string url"""
    return normalize(UNICODE_NORMAL_FORM, tag.find('a').get('href'))
