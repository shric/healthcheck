from psycopg2.extras import RealDictCursor
import psycopg2
from datetime import datetime


class PostgreSQLOutput:
    def __init__(self, config):
        self.config = config
        self.db = psycopg2.connect(self.config['dsn'])

    def create_or_get_url_id(self, url):
        """Get an url_id from the database, add the entry if the url does not exist."""

        # There are many alternative ways to do this compared to a SELECT/INSERT
        # which could suffer from a race, but the implementations are far less trivial.
        # See https://stackoverflow.com/questions/34708509/how-to-use-returning-with-on-conflict-in-postgresql
        c = self.db.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT id FROM urls WHERE url=%s", (url,))
        res = c.fetchone()
        if res is not None:
            return res['id']
        else:
            c.execute("INSERT INTO urls (url) VALUES(%s) RETURNING id", (url,))
            self.db.commit()
            return c.fetchone()['id']

    def send(self, result):
        url_id = self.create_or_get_url_id(result.url)

        c = self.db.cursor(cursor_factory=RealDictCursor)
        c.execute("INSERT INTO scrape_results (url_id, scrape_time, status_code, matched, response_time, error) "
                  "VALUES (%s, %s, %s, %s, %s, %s)",
                  (url_id, datetime.utcfromtimestamp(result.scrape_time), result.status_code, result.matched, result.response_time, result.error))
        self.db.commit()
