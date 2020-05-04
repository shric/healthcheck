from kafka import KafkaConsumer
from collections import ChainMap
import scraper


class KafkaInput:
    def __init__(self, config):
        self.config = config
        self.topic = config['topic']
        self.consumer = KafkaConsumer(self.topic,
                                      **ChainMap(config['config'],
                                                 config['consumer']))

    def recv(self):
        raw_msgs = self.consumer.poll(timeout_ms=1000)
        for tp, msgs in raw_msgs.items():
            for msg in msgs:
                r = scraper.ScrapeResult()
                r.deserialize(msg.value)
                yield r
        self.consumer.commit()
