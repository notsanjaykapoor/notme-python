import prefect
import ulid

import kafka
import models


@prefect.task()
def rp_up_consume_task(topic: str, group: str, key: str) -> int:
    """consume redpanda up message"""

    code = -1

    consumer = kafka.consumer(topic=topic, group=group)

    consumer_timeout = 2.0
    consumer_exhausted = 20.0
    consumer_waited = 0.0

    while True:
        msg = consumer.poll(timeout=consumer_timeout)

        if msg is None:
            consumer_waited += consumer_timeout

            if consumer_waited >= consumer_exhausted:
                code = 404
                break

            print(f"rp_up_consume_task topic {topic} group {group} waiting")

            continue

        if msg.error():
            pass  # todo

        kafka_msg = models.KafkaMessage(msg)

        if kafka_msg.key_str() == key:
            code = 0
            break

    consumer.close()

    return code


@prefect.task()
def rp_up_send_task(topic: str) -> str:
    """send redpanda up message"""

    writer = kafka.Writer(topic=topic)
    key = ulid.new().str
    message = {
        "name": "up_check",
    }

    # write message to kafka stream
    writer.call(key=key, message=message)

    return key
