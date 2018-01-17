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
    media_id = peewee.ForeignKeyField(media, to_field='media_id')
    comment_text = peewee.CharField ()

    class Meta:
        database = database


class self_comment (peewee.Model):
    comment_id = peewee.CharField(unique=True)
    media_id = peewee.ForeignKeyField(media, to_field='media_id')
    comment_text = peewee.CharField ()
    positive_sentiments = peewee.IntegerField()
    negative_sentiments = peewee.IntegerField()
    classification = peewee.CharField()

    class Meta:
        database = database


class likers_list (peewee.Model):
    user_id = peewee.ForeignKeyField(user, to_field='user_id')
    media_id = peewee.ForeignKeyField(media, to_field='media_id')
    liker_username = peewee.CharField()

    class Meta:
        database = database


class recent_liked_posts (peewee.Model):
    media_id = peewee.ForeignKeyField(media, to_field='media_id')
    media_type = peewee.CharField()
    media_link = peewee.CharField()
    likes = peewee.IntegerField()
    comment_count = peewee.IntegerField()

    class Meta:
        database = database


def initialize_db():
    database.create_tables ([user, media, comments, self_comment, likers_list,recent_liked_posts], safe=True)


initialize_db()
