import os
import pika
import time
import docker

import logging
logger = logging.getLogger(__name__)

from pyrabbit.api import Client

from ..helpers import UnpackHelpers

cl = Client(f'http://{os.environ["UNPACK_HOST"]}:55672/api', 'guest', 'guest')


def main(queue_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.environ['UNPACK_HOST'])
    )
    channel = connection.channel()

    fetcher_queue_name = f'fetch-{queue_id}'
    broadcaster_queue_name = f'broadcast-{queue_id}'

    fetcher_q = channel.queue_declare(queue=fetcher_queue_name)
    broadcaster_q = channel.queue_declare(queue=broadcaster_queue_name)

    logger.info(f'Creating queues for id: {queue_id}')

    # docker_client = docker.from_env()
    empty_since = None
    queue_ttl = 10 * 60
    check_queue_rate = 2
    containers = []

    # Workers to create
    broadcast_container = UnpackHelpers.start_docker_container(
        container_name=UnpackHelpers.DOCKER_CONTAINER_NAMES['QUEUE_BROADCAST_WORKER'],
        queue_name=broadcaster_queue_name,
    )
    containers.append(broadcast_container)

    for i in range(5):
        fetcher_container = UnpackHelpers.start_docker_container(
            container_name=UnpackHelpers.DOCKER_CONTAINER_NAMES['QUEUE_FETCHER_WORKER'],
            queue_name=fetcher_queue_name,
        )
        containers.append(fetcher_container)

    # As long as queue has data in it and the TTL has not been reached
    while True:
        if empty_since is not None and (time.time() - empty_since) >= queue_ttl:
            break

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
