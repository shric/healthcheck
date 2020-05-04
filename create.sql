CREATE TABLE IF NOT EXISTS urls(
	id serial PRIMARY KEY,
	url text UNIQUE);

CREATE TABLE IF NOT EXISTS scrape_results(
	id serial PRIMARY KEY,
	url_id integer NOT NULL references urls(id),
	scrape_time timestamp without time zone,
	status_code integer,
	matched boolean,
	response_time real,
	error text);

CREATE USER storer WITH PASSWORD 'abcdef';

GRANT SELECT, INSERT ON urls, scrape_results TO storer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO storer; 
