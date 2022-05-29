import asyncio
import json
import logging
import sys
import typing

from dataclasses import dataclass

from confluent_kafka import Consumer, KafkaError, KafkaException
from kafka.config import config_reader

from models.actor_message import ActorMessage


@dataclass
class Struct:
    code: int
    errors: list[str]


class KafkaReader:
    def __init__(self, topic: str, group: str, handler: typing.Any):
        self._topic = topic
        self._group = group
        self._handler = handler

        config_reader["group.id"] = self._group

        self._consumer = Consumer(config_reader)
        self._timeout = 1.0
        self._topics = []
        self._logger = logging.getLogger("service")
        self._task = asyncio.current_task()

        self._topics.append(self._topic)

        if self._task is not None:
            self._log_subject = f"actor '{self._task.get_name()}' {__name__}"
        else:
            self._log_subject = f"{__name__}"

    async def call(self):
        struct = Struct(0, [])

        self._logger.info(f"{self._log_subject} reading topics {self._topics}")

        try:
            self._consumer.subscribe(self._topics)

            while True:
                msg = self._consumer.poll(timeout=self._timeout)

                if msg is None:
                    await self._asyncio_yield()
                    continue

                if msg.error():
                    # whoops, some type of read error
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        self._logger.info(f"{self._log_subject} partition eof")
                        # todo:
                        continue
                    elif msg.error():
                        raise KafkaException(msg.error())

                # call handler to process message
                handler_struct = self._handler.call(msg=ActorMessage(msg))

                # check return code and ack
                if handler_struct.code == 0:
                    self._logger.info(f"{self._log_subject} ack")
                    self._consumer.commit(asynchronous=False)

                await self._asyncio_yield()
        except KafkaException as e:
            self._logger.error(f"{self._log_subject} exception {e}")
        except asyncio.exceptions.CancelledError:
            self._logger.error(f"{self._log_subject} cancelled exception")
        except Exception as e:
            self._logger.error(f"{self._log_subject} exception {e}")
        except:  # e.g. keyboard interrupt
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
