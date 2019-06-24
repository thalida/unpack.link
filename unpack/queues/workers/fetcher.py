import os
os.environ['TZ'] = 'UTC'

import logging
logger = logging.getLogger(__name__)

import pika

from unpack.queues.jobs.fetcher import Fetcher


def main(queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.environ['MQ_HOST'])
    )
    channel = connection.channel()

    channel.basic_consume(queue=queue_name, on_message_callback=Fetcher)


    print(' [*] Waiting for Fetcher messages. To exit press CTRL+C or delete the queue')
    channel.start_consuming()
