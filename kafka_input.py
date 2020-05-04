import scraper


class KafkaInput:
    """Simple Kafka consumer

    Consumes messages from a single topic, expects the messages to be a serialized
    scraper.ScrapeResult
    """

    def __init__(self, consumer):
        """
        :param consumer: a KafkaConsumer
        """
        self.consumer = consumer

    def recv(self):
        """
        Receives messages from provided consumer.

        :return: a scraper.ScrapeResult
        """
        raw_msgs = self.consumer.poll(timeout_ms=1000)
        for tp, msgs in raw_msgs.items():
            for msg in msgs:
                r = scraper.ScrapeResult()
                r.deserialize(msg.value)
                yield r
        self.consumer.commit()
