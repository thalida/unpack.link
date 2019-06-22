import os
os.environ['TZ'] = 'UTC'

import pika

from unpack.queues.fetcher.worker import Fetcher


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()
    channel.queue_declare(queue='fetcher_p0', durable=True)
    print('[*] Waiting for Fetcher (Priority 0) messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='fetcher_p0',
        on_message_callback=Fetcher
    )

    channel.start_consuming()


if __name__ == '__main__':
    main()
