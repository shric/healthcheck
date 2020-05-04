import logging
import logging.config
import toml
import kafka_input
import postgresql_output

import psycopg2

class Storer:
    def __init__(self, input, output):
        self.input = input
        self.output = output

    def run(self):
        while True:
            for msg in self.input.recv():
                self.output.send(msg)


def main():
    logging.config.fileConfig('logging.conf')
    config = toml.load('config.toml')

    db = psycopg2.connect(config['postgresql']['dsn'])
    s = Storer(kafka_input.KafkaInput(config['kafka']),
               postgresql_output.PostgreSQLOutput(db))
    s.run()


if __name__ == '__main__':
    main()
