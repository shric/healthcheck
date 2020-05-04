import logging
import logging.config
import toml
import kafka_input
import postgresql_output


class Storer:
    def __init__(self, input, output, config):
        self.input = input
        self.output = output
        self.config = config

    def run(self):
        while True:
            for msg in self.input.recv():
                self.output.send(msg)


def main():
    logging.config.fileConfig('logging.conf')
    config = toml.load('config.toml')

    s = Storer(kafka_input.KafkaInput(config['kafka']),
               postgresql_output.PostgreSQLOutput(config['postgresql']),
               config['store'])
    s.run()


if __name__ == '__main__':
    main()
