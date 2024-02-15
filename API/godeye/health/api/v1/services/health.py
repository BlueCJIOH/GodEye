import logging

import psycopg2
from asgiref.sync import async_to_sync
from channels_redis.core import RedisChannelLayer

from godeye.settings import CHANNEL_LAYERS, DATABASES

logger = logging.getLogger("main")


def check_db_health():
    try:
        conn = psycopg2.connect(
            database=f'{DATABASES["default"]["NAME"]}',
            user=f'{DATABASES["default"]["USER"]}',
            password=f'{DATABASES["default"]["PASSWORD"]}',
            host=f'{DATABASES["default"]["HOST"]}',
            port=f'{DATABASES["default"]["PORT"]}',
        )
        cursor = conn.cursor()
        cursor.execute(
            """SELECT table_name
                            FROM information_schema.tables
                           WHERE table_schema = 'public'
                       """
        )
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("The database connection was successfully established.")
        return "The database connection was successfully established."
    except psycopg2.Error as err:
        logger.critical(f"Failed to connect to the database: {err}!")
        return f"Failed to connect to the database: {err}!"


def check_redis_health():
    host = CHANNEL_LAYERS["default"]["CONFIG"]["hosts"]
    try:
        channel_layer = RedisChannelLayer(hosts=host)
        channel_name = async_to_sync(channel_layer.new_channel)()
        async_to_sync(channel_layer.send)(
            channel_name,
            {
                "type": "test.message",
                "text": "The redis channel connection was successfully established.",
            },
        )
        message = async_to_sync(channel_layer.receive)(channel_name)
        logger.info(message["text"])
        return message["text"]
    except:
        logger.critical("Failed to connect to the redis channel!")
        return "Failed to connect to the redis channel!"
