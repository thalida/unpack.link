import os
os.environ['TZ'] = 'UTC'

import logging
logger = logging.getLogger(__name__)

import pika

from unpack.queues.jobs.fetcher import Fetcher


def main(queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.environ['UNPACK_HOST'])
    )
    channel = connection.channel()

    channel.basic_qos(prefetch_count=5)
    channel.basic_consume(queue=queue_name, on_message_callback=Fetcher)


    logger.info(' [*] Waiting for Fetcher messages. To exit press CTRL+C or delete the queue')
    channel.start_consuming()
