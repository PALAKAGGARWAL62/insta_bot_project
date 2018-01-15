import peewee

database = peewee.SqliteDatabase ('instabot.db')


class user (peewee.Model):
    user_id = peewee.CharField (unique=True)
    user_name = peewee.CharField ()
    follows_count = peewee.IntegerField ()
    fullname = peewee.CharField ()
    followed_by_count = peewee.IntegerField ()

    class Meta:
        database = database


class media (peewee.Model):
    user_id = peewee.ForeignKeyField(user, to_field='user_id')
    media_id = peewee.CharField (unique=True)
    media_type = peewee.CharField ()
    media_link = peewee.CharField()
    likes = peewee.IntegerField()
    comment_count = peewee.IntegerField()

    class Meta:
        database = database


class comments (peewee.Model):
    comment_id = peewee.CharField (unique=True)
    user_id = peewee.ForeignKeyField(user, to_field='user_id')
    media_id = peewee.ForeignKeyField(media,to_field='media_id')
    comment_text = peewee.CharField ()

    class Meta:
        database = database


def initialize_db():
    database.create_tables ([user, media, comments], safe=True)


initialize_db()
