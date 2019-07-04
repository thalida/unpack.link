import os
os.environ['TZ'] = 'UTC'

import logging
logger = logging.getLogger(__name__)

import pika

from unpack.queues.jobs.fetcher import Fetcher


def handle_message_callback(*args, **kwargs):
    if os.environ['UNPACK_DEV_PROFILER'] == 'TRUE':
        import cProfile
        profiler = cProfile.Profile()
        profiler.enable()

    Fetcher(*args, **kwargs)

    if os.environ['UNPACK_DEV_PROFILER'] == 'TRUE':
        profiler.disable()
        profiler.dump_stats(f'/tmp/unpack_profiler_results.txt')

def main(queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.environ['UNPACK_HOST'])
    )
    channel = connection.channel()

    channel.basic_qos(prefetch_count=5)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=handle_message_callback
    )


    logger.info(' [*] Waiting for Fetcher messages. To exit press CTRL+C or delete the queue')
    channel.start_consuming()
