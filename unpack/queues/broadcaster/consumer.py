import os
os.environ['TZ'] = 'UTC'

import pika

from unpack.queues.broadcaster.worker import Broadcaster


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()
    channel.queue_declare(queue='broadcaster', durable=True)
    print(' [*] Waiting for Broadcaster messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='broadcaster',
        on_message_callback=Broadcaster,
        auto_ack=True
    )

    channel.start_consuming()

if __name__ == '__main__':
    main()
