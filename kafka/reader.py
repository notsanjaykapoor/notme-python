import asyncio
import dataclasses
import sys

import confluent_kafka

import kafka.config
import log
import models


@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


class Reader:
    def __init__(self, topic: str, group: str, handler: kafka.Handler):
        self._topic = topic
        self._group = group
        self._handler = handler

        kafka.config.config_reader["group.id"] = self._group

        self._consumer = confluent_kafka.Consumer(kafka.config.config_reader)
        self._timeout = 1.0
        self._topics = [self._topic]
        self._logger = log.init("service")

    async def call(self):
        struct = Struct(0, [])

        self._task = asyncio.current_task()
        self._log_subject = f"actor '{self._task.get_name()}' {__name__}"

        # create default actor used for callback during message processing
        self._actor = models.Actor(name=self._task.get_name(), handler=self)

        self._logger.info(f"{self._log_subject} listening topics {self._topics}")

        try:
            self._consumer.subscribe(self._topics)

            while True:
                msg = self._consumer.poll(timeout=self._timeout)

                if msg is None:
                    await self._asyncio_yield()
                    continue

                if msg.error():
                    # whoops, some type of read error
                    if msg.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
                        self._logger.info(f"{self._log_subject} partition eof")
                        # todo:
                        continue
                    elif msg.error():
                        raise confluent_kafka.KafkaException(msg.error())

                # call handler to process message
                struct_handler = await self._handler.call(
                    msg=models.KafkaMessage(msg),
                )

                # check return code and ack
                if struct_handler.code == 0:
                    self._logger.info(f"{self._log_subject} ack")
                    self._consumer.commit(asynchronous=False)

                await self._asyncio_yield()
        except confluent_kafka.KafkaException as e:
            self._logger.error(f"{self._log_subject} exception {e}")
        except asyncio.exceptions.CancelledError:
            self._logger.error(f"{self._log_subject} cancelled exception")
        except Exception as e:
            self._logger.error(f"{self._log_subject} exception {e}")
        except KeyboardInterrupt:  # e.g. keyboard interrupt like ctrl^c
            self._logger.error(f"{self._log_subject} exception {sys.exc_info()[0]}")
            raise
        finally:
            self._consumer.close()
            self._logger.info(f"{self._log_subject} exiting")

        return struct

    # play nicely with asyncio
    async def _asyncio_yield(self, seconds: float = 0.1) -> int:
        if self._task is None:
            return 0

        await asyncio.sleep(seconds)

        return 0
