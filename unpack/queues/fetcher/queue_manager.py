import os
import pika
import time
import docker

import logging
logger = logging.getLogger(__name__)

def main(queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(os.environ['MQ_HOST'])
    )
    channel = connection.channel()
    q = channel.queue_declare(queue=queue_name)

    print(f'create queue: {queue_name}')

    docker_client = docker.from_env()
    empty_since = None
    queue_ttl = 10
    check_queue_rate = 2

    # Workers to create
    for i in range(5):
        hostname = f'worker_{queue_name}_{i}'
        docker_client.containers.run(
            image="unpack_container",
            command=f"fetcher-queue-worker -q {queue_name}",
            hostname=hostname,
            environment={
                'MQ_HOST': os.environ['MQ_HOST'],
                'UNPACK_DB_NAME': os.environ['UNPACK_DB_NAME'],
                'UNPACK_DB_USER': os.environ['UNPACK_DB_USER'],
                'UNPACK_DB_PASSWORD': os.getenv('UNPACK_DB_PASSWORD'),
            },
            volumes={
                '/tmp/unpack_worker_logs.log': {'bind': '/tmp/unpack_controller_logs.log', 'mode': 'rw'},
            },
            detach=True
        )

    # As long as queue has data in it and the TTL has not been reached
    while empty_since is None or (time.time() - empty_since) < queue_ttl:
        # No need to check to often, this just helps clean things up
        time.sleep(check_queue_rate)
        q_len = q.method.message_count
        if q_len == 0 and empty_since is None:
            empty_since = time.time()
        elif q_len > 0:
            empty_since = None

    # The queue has been empty for the TTL, so lets delete it,
    # which will kill all the workers
    print("Delete stale queue")
    channel.queue_delete(queue=queue_name)
