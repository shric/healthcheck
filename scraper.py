#!/usr/bin/env python3
from collections import ChainMap
from datetime import datetime
import logging.config
import time
import logging
import re
import json

import requests
import toml

import kafka_output

DEFAULT_SCRAPER_OPTIONS = {
    'frequency': 60,
}

DEFAULT_REQUEST_OPTIONS = {
    'timeout': 15,
}


def unixtime_to_str(unixtime):
    # https://stackoverflow.com/a/3682808
    return datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')


class ScrapeResult:
    """
    A class to store results from Scraper, provides serialize and deserialize helpers.
    """
    def __init__(self, url=None, scrape_time=None, status_code=None, matched=None, response_time=None, error=None):
        """

        :param url: The URL that was scraped.
        :param scrape_time: The time in unixtime format when the scrape occurred.
        :param status_code: The http status code of the scrape.
        :param matched: Whether the http get text matched a given pattern (None of no pattern given)
        :param response_time: The amount of time it took to make the scrape.
        :param error: Any request.get error string.
        """
        self.scrape_time = scrape_time
        self.url = url
        self.status_code = status_code
        self.matched = matched
        self.response_time = response_time
        self.error = error
        pass

    def deserialize(self, string):
        """
        Deserializes a string of a scrape result.

        :param string: A JSON string containing the ScrapeResult attributes.
        :return: A ScrapeResult deserialized from the string.
        """
        result = json.loads(string)
        for k in ['url', 'status_code', 'matched', 'response_time', 'error', 'scrape_time']:
            setattr(self, k, result[k])
        return self

    def serialize(self):
        """
        Serializes a ScrapeResult to a string

        :return: A JSON string
        """
        return str.encode(json.dumps(self.__dict__))

    def __repr__(self):
        result = f"{unixtime_to_str(self.scrape_time)}: {self.url}: "
        if self.error is not None:
            result += self.error
        else:
            result += "{status_code} {matched} {response_time}".format(**vars(self))
        return result


class Scraper:
    def __init__(self, output, config):
        """

        :param output: An output class which implements a send(msg) function.
        :param config: A config dict containing 'request' and 'scraper' keys and a list of URLs.
        e.g.
        {'scraper': {'frequency': 60},
         'request': {'timeout': 10},

         # This timeout overrides the above
         'https://www.google.com': {'request': {'timeout': 5}},
         'https://news.ycombinator.com: {'pattern': 'Hacker N.*'},
        }

        frequency: The number of seconds to sleep between scrapes.
        request: a dict containing any kwargs options passed to requests.get
        pattern: an optional regex to search for.

        """
        self.output = output
        self.request_options = config.pop('request', None)
        self.scraper_options = config.pop('scraper', None)
        self.scrapes = config
        pass

    def run(self):
        scraper_options = ChainMap(self.scraper_options, DEFAULT_SCRAPER_OPTIONS)
        while True:
            for url, options in self.scrapes.items():
                logging.debug("%s: %s", url, options)
                request_options = ChainMap(options.get('request', {}), self.request_options, DEFAULT_REQUEST_OPTIONS)
                pattern = options.get('pattern', None)
                matched = None
                if pattern is not None:
                    pattern = re.compile(pattern)
                if not request_options.get("verify", True):
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

                scrape_time = time.time()
                try:
                    response = requests.get(url, **request_options)
                except Exception as e:
                    logging.error("Error for %s: %s", url, e)
                    result = ScrapeResult(url=url, scrape_time=scrape_time, error=str(e))
                    pass
                else:
                    if pattern is not None:
                        matched = bool(pattern.search(response.text))
                    result = ScrapeResult(url=url, scrape_time=scrape_time, matched=matched,
                                          response_time=response.elapsed.total_seconds(),
                                          status_code=response.status_code)
                logging.debug("Result: %s", result)
                self.output.send(result)
            if scraper_options.get('run_once', False):
                return
            time.sleep(scraper_options['frequency'])


def main():
    logging.config.fileConfig('logging.conf')
    config = toml.load('config.toml')

    s = Scraper(kafka_output.KafkaOutput(config['kafka']),
                config['scrape'])
    s.run()


if __name__ == '__main__':
    main()
