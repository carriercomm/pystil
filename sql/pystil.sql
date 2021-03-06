CREATE ROLE pystil LOGIN PASSWORD 'pystil' VALID UNTIL 'infinity';
CREATE DATABASE pystil WITH ENCODING='UTF8' OWNER=pystil TEMPLATE=template0 CONNECTION LIMIT=-1;

\connect pystil;

-- Table: visit
DROP TABLE IF EXISTS visit;

CREATE TABLE visit
(
  id serial,
  browser_name character varying,
  browser_version character varying,
  date timestamp without time zone,
  hash character varying,
  host character varying,
  ip character varying,
  "language" character varying,
  last_visit timestamp without time zone,
  page character varying,
  platform character varying,
  query character varying,
  referrer character varying,
  referrer_domain character varying,
  pretty_referrer character varying,
  site character varying,
  size character varying,
  "time" interval,
  uuid character varying NOT NULL,
  client_tz_offset integer,
  country character varying,
  country_code character varying,
  city character varying,
  lat numeric,
  lng numeric,
  asn varchar,
  CONSTRAINT pk PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

ALTER TABLE visit OWNER TO pystil;

-- Index: btrees

DROP INDEX IF EXISTS btrees;

CREATE INDEX btrees
  ON visit
  USING btree
  (host, date);


\i aggregates.sql
