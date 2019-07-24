from ..log import *
import os
import pika
import time
import docker
import json

import logging
logger = logging.getLogger(__name__)

import requests
import urllib.parse

from ..helpers import UnpackHelpers

rabbitmq_api_url = f'http://{os.environ["UNPACK_HOST"]}:15672/api'
rabbitmq_auth = ('guest', 'guest')
rabbitmq_vhost = '/'

def quote(string):
    return urllib.parse.quote(string, safe='')


def get_queue_message_count(queue_name):
    req_url = f'{rabbitmq_api_url}/queues/{quote(rabbitmq_vhost)}/{quote(queue_name)}'
    json_res = requests.get(req_url, auth=rabbitmq_auth).json()
    return json_res.get('messages', 0)


def publish_broadcast(channel, queue_name, event_name, **kwargs):
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps({
            'event_name': event_name,
            'data': kwargs,
        }, default=str),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))


def tick(channel, fetcher_queue_name, broadcaster_queue_name, empty_since, check_queue_rate):
    time.sleep(check_queue_rate)

    publish_broadcast(
        channel=channel,
        queue_name=broadcaster_queue_name,
        event_name=UnpackHelpers.EVENT_NAME['REQUEST:HEARTBEAT']
    )

    fetcher_q_len = get_queue_message_count(fetcher_queue_name)
    broadcaster_q_len = get_queue_message_count(broadcaster_queue_name)
    total_q = fetcher_q_len + broadcaster_q_len

    if (total_q == 0) and (empty_since is None):
        empty_since = time.time()
    elif total_q > 0:
        empty_since = None

    return empty_since


def handleEmptyQueue(channel, request_id, containers, fetcher_queue_name, broadcaster_queue_name):
    publish_broadcast(
        channel=channel,
        queue_name=broadcaster_queue_name,
        event_name=UnpackHelpers.EVENT_NAME['REQUEST:COMPLETED']
    )

    time.sleep(2)

    for container in containers:
        container.remove(force=True)

    channel.queue_delete(queue=fetcher_queue_name)
    channel.queue_delete(queue=broadcaster_queue_name)

    # The queue has been empty for the TTL, so lets delete it,
    # which will kill all the workers
    logger.info(f'Delete stale queues for id: {request_id}')


def main(request_id):
    empty_since = None
    queue_ttl = 1 * 30
    check_queue_rate = 5
    containers = []

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.environ['UNPACK_HOST'])
    )

    channel = connection.channel()

    fetcher_queue_name = UnpackHelpers.get_queue_name(
        queue_type='fetch',
        request_id=request_id
    )

    broadcaster_queue_name = UnpackHelpers.get_queue_name(
        queue_type='broadcast',
        request_id=request_id
    )

    fetcher_q = channel.queue_declare(queue=fetcher_queue_name)
    broadcaster_q = channel.queue_declare(queue=broadcaster_queue_name)

    publish_broadcast(
        channel=channel,
        queue_name=broadcaster_queue_name,
        event_name=UnpackHelpers.EVENT_NAME['REQUEST:IN_PROGRESS']
    )

    logger.info(f'Creating queues for id: {request_id}')

    # Workers to create
    broadcast_container = UnpackHelpers.start_docker_container(
        container_name=UnpackHelpers.DOCKER_CONTAINER_NAMES['QUEUE_BROADCAST_WORKER'],
        request_id=request_id,
    )
    containers.append(broadcast_container)

    for i in range(10):
        fetcher_container = UnpackHelpers.start_docker_container(
            container_name=UnpackHelpers.DOCKER_CONTAINER_NAMES['QUEUE_FETCHER_WORKER'],
            request_id=request_id,
        )
        logger.info(f'created container: {fetcher_container}')
        containers.append(fetcher_container)

    logger.info(f'created containers: {containers}')

    # As long as queue has data in it and the TTL has not been reached
    while True:
        if empty_since is not None and (time.time() - empty_since) >= queue_ttl:
            handleEmptyQueue(
                channel=channel,
                request_id=request_id,
                containers=containers,
                fetcher_queue_name=fetcher_queue_name,
                broadcaster_queue_name=broadcaster_queue_name,
            )
            break

        empty_since = tick(
            channel=channel,
            fetcher_queue_name=fetcher_queue_name,
            broadcaster_queue_name=broadcaster_queue_name,
            empty_since=empty_since,
            check_queue_rate=check_queue_rate
        )
