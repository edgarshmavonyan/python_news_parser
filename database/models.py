from peewee import *
import datetime
from playhouse.sqlite_ext import JSONField


news_db = SqliteDatabase('news_db.db')
STANDARD_MAX_URL_LENGTH = 2084
DEFAULT_DATE = datetime.datetime(1970, 1, 1)


class NewsModel(Model):
    class Meta:
        database = news_db


class Section(NewsModel):
    name = FixedCharField()
    url = CharField(max_length=STANDARD_MAX_URL_LENGTH)
    description = TextField()
    last_update = DateTimeField(default=DEFAULT_DATE)

    def __repr__(self):
        return self.name


class Tag(NewsModel):
    name = FixedCharField(primary_key=True)

    def __repr__(self):
        return self.name


class Article(NewsModel):
    title = FixedCharField()
    section = ForeignKeyField(Section, backref='articles')
    url = CharField(max_length=STANDARD_MAX_URL_LENGTH)
    last_update = DateTimeField()
    text = TextField()
    tags = ManyToManyField(Tag, backref='articles')
    length_distribution = TextField()
    words_distribution = TextField()

    def __repr__(self):
        return str(self.section) + ': ' + self.title + '; ' + str(self.last_update)
