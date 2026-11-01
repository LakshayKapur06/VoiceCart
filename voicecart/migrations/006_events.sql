CREATE TABLE application_events (
 event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 kind text NOT NULL,
 outcome text NOT NULL,
 environment text NOT NULL CHECK (environment IN ('test','development','merchant')),
 duration_ms integer NOT NULL CHECK (duration_ms >= 0),
 timings jsonb NOT NULL DEFAULT '[]',
 occurred_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX application_events_time ON application_events(occurred_at);
