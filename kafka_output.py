from kafka import KafkaProducer
import logging


class KafkaOutput:
    def __init__(self, config):
        self.config = config
        self.producer = KafkaProducer(**config['config'])

    def send(self, result):
        payload = result.serialize()
        logging.debug(payload)
        self.producer.send(self.config['topic'], payload)
        self.producer.flush()
