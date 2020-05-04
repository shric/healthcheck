[![Build Status](https://travis-ci.org/shric/healthcheck.svg?branch=master)](https://travis-ci.org/shric/healthcheck)

# Healthcheck

A utility to scrape a list of websites and place the results in a PostgreSQL
database using Kafka as an event log.

There are two scripts to run:

## Scraper

`scraper.py` scrapes specified websites and sends the following details as a
JSON string to Kafka:

- URL
- The time the URL was scraped
- The HTTP status code returned
- Whether the text matched a specified pattern (or null if no pattern specified)
- The total time it took to scrape the URL

or

- URL
- Any error encountered retrieving the URL's content

Example payload:

```json
{"scrape_time": 1588631906.967833,
 "url": "https://www.google.com",
 "status_code": 200,
 "matched": null,
 "response_time": 0.259916,
 "error": null}
```

## Storer

`storer.py` consumes JSON messages from Scraper as described above from Kafka
and feeds them to a PostgreSQL database.

## Configuration

Both scripts expect a `config.toml`. Example:

```toml
[kafka]
topic = "healthcheck"
# Anything beginning with config is passed to both scraper and storer in order
# to connect to Kafka
config.bootstrap_servers="kafka:9092"
config.security_protocol="SSL"
config.ssl_cafile="ca.pem"
config.ssl_certfile="service.cert"
config.ssl_keyfile="service.key"
# These options are used by storer to configure the consumer
consumer.auto_offset_reset="earliest"
consumer.client_id="storer"
consumer.group_id="storer"

[postgresql]
dsn = "postgres://user:password@postgresql:5432/database?sslmode=require"

# Global scrape options, currently just scrape frequency. Default is 60 seconds.
[scrape.scraper]
frequency=5

# Global request options, passed to requests.get. Default timeout is 15 seconds.
[scrape.request]
timeout=10

# Each URL stanza can override the global request options
[scrape."https://www.google.com"]
request.timeout=1

[scrape."https://ramblings.implicit.net"]
request.timeout=5
# Optionally look for a regex within the text.
pattern="functions that.*"

[scrape."https://expired.badssl.com/"]
request.verify=false

[scrape."https://wrong.host.badssl.com/"]
```

## Limitations, caveats and TODOs

- No partitions or sharding has been considered for the PostgreSQL database.
  A single table is used for all results. The URLs are stored in a separate table. See `create.sql`.
  
- Unit tests have yet to be written for `postgresql_output.py`.

- Packaging with e.g. `setuptools`.

- Dockerfiles

- Command line argument parsing with e.g. `argparse` to specify configuration, uses `config.toml` instead.
