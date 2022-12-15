import prefect

import kafka
import models


@prefect.task(log_prints=True)
def rp_up_consume(topic: str, group: str, key: str) -> int:
    """consume redpanda up message"""

    code = -1

    consumer = kafka.consumer(topic=topic, group=group)

    # wait up to 20 seconds for message
    consumer_timeout = 2.0
    consumer_exhausted = 20.0
    consumer_waited = 0.0

    while True:
        msg = consumer.poll(timeout=consumer_timeout)

        if msg is None:
            consumer_waited += consumer_timeout

            if consumer_waited >= consumer_exhausted:
                code = 408
                print(f"topic '{topic}' group '{group}' timeout")
                break

            print(f"topic '{topic}' group '{group}' polling")

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
def rp_up_send(topic: str, key: str) -> int:
    """send redpanda up message"""

    writer = kafka.Writer(topic=topic)

    message = {
        "name": "up_check",
    }

    writer.call(key=key, message=message)

    return 0
