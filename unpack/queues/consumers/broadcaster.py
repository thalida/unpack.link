import os
os.environ['TZ'] = 'UTC'

import logging
logger = logging.getLogger(__name__)

import pika
from retry import retry

from unpack.helpers import UnpackHelpers
from unpack.queues.workers.broadcaster import Broadcaster


def handle_message_callback(*args, **kwargs):
    if os.environ['UNPACK_DEV_PROFILER'] == 'TRUE':
        import cProfile
        profiler = cProfile.Profile()
        profiler.enable()

    Broadcaster(*args, **kwargs)

    if os.environ['UNPACK_DEV_PROFILER'] == 'TRUE':
        profiler.disable()
        profiler.dump_stats(f'/tmp/unpack_profiler_results.txt')


@retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
def main(request_id):
    queue_name = UnpackHelpers.get_queue_name(
        queue_type='broadcast',
        request_id=request_id
    )
    connection_params = pika.ConnectionParameters(
        os.environ['UNPACK_HOST'],
        heartbeat=4*60,
        blocked_connection_timeout=2*60
    )
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=handle_message_callback,
        auto_ack=True
    )

    try:
        logger.info(' [*] Waiting for Broadcaster messages. To exit press CTRL+C or delete the queue')
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()
    except pika.exceptions.ConnectionClosedByBroker:
        pass
