import confluent_kafka

import kafka.config


def consumer(topic: str, group: str) -> confluent_kafka.Consumer:
    """create kafka consumer and subscribe to topic"""
    consumer_ = confluent_kafka.Consumer(kafka.config.config_reader(group_id=group))
    consumer_.subscribe([topic])

    return consumer_
