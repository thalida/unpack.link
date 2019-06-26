import os
import pika
import time
import docker

import logging
logger = logging.getLogger(__name__)

from pyrabbit.api import Client

cl = Client(f'http://{os.environ["MQ_HOST"]}:55672/api', 'guest', 'guest')

def main(queue_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.environ['MQ_HOST'])
    )
    channel = connection.channel()

    fetcher_queue_name = f'fetch-{queue_id}'
    broadcaster_queue_name = f'broadcast-{queue_id}'

    fetcher_q = channel.queue_declare(queue=fetcher_queue_name)
    broadcaster_q = channel.queue_declare(queue=broadcaster_queue_name)

    logger.info(f'Creating queues for id: {queue_id}')

    docker_client = docker.from_env()
    empty_since = None
    queue_ttl = 5 * 60
    check_queue_rate = 2
    containers = []

    broadcast_container = docker_client.containers.run(
        image="unpack_container",
        command=f"queue-broadcast-worker -q {broadcaster_queue_name}",
        environment={
            'MQ_HOST': os.environ['MQ_HOST'],
            'UNPACK_DB_NAME': os.environ['UNPACK_DB_NAME'],
            'UNPACK_DB_USER': os.environ['UNPACK_DB_USER'],
            'UNPACK_DB_PASSWORD': os.getenv('UNPACK_DB_PASSWORD'),
        },
        volumes={
            '/tmp/unpack_broadcast_worker_logs.log': {'bind': '/tmp/unpack_controller_logs.log', 'mode': 'rw'},
        },
        detach=True,
        auto_remove=True,
    )
    containers.append(broadcast_container)

    # Workers to create
    for i in range(5):
        fetcher_container = docker_client.containers.run(
            image="unpack_container",
            command=f"queue-fetcher-worker -q {fetcher_queue_name}",
            environment={
                'MQ_HOST': os.environ['MQ_HOST'],
                'UNPACK_DB_NAME': os.environ['UNPACK_DB_NAME'],
                'UNPACK_DB_USER': os.environ['UNPACK_DB_USER'],
                'UNPACK_DB_PASSWORD': os.getenv('UNPACK_DB_PASSWORD'),
            },
            volumes={
                '/tmp/unpack_fetcher_worker_logs.log': {'bind': '/tmp/unpack_controller_logs.log', 'mode': 'rw'},
            },
            detach=True,
            auto_remove=True,
        )
        containers.append(fetcher_container)

    # As long as queue has data in it and the TTL has not been reached
    while (empty_since is None) or (empty_since is not None and (time.time() - empty_since) < queue_ttl):
        # No need to check to often, this just helps clean things up
        time.sleep(check_queue_rate)

        # redeclearing the queue
        fetcher_q_len = channel.queue_declare(queue=fetcher_queue_name).method.message_count
        broadcaster_q_len = channel.queue_declare(queue=broadcaster_queue_name).method.message_count
        total_q = fetcher_q_len + broadcaster_q_len

        if (total_q == 0) and (empty_since is None):
            empty_since = time.time()
        elif fetcher_q_len > 0 or broadcaster_q_len > 0:
            empty_since = None


    for container in containers:
        container.remove(force=True)

    channel.queue_delete(queue=fetcher_queue_name)
    channel.queue_delete(queue=broadcaster_queue_name)

    # The queue has been empty for the TTL, so lets delete it,
    # which will kill all the workers
    logger.info("Delete stale queue")