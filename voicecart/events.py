"""Actual minimal aggregate events; no transcript, query, IP or credentials."""

from datetime import UTC, datetime, timedelta

from psycopg.types.json import Jsonb


class EventStore:
    def __init__(self, database, environment="development"):
        if environment not in ("test", "development", "merchant"):
            raise ValueError("Invalid event environment")
        self.database = database
        self.environment = environment

    def record(self, kind, outcome, seconds, spans=()):
        with self.database.connect() as connection:
            connection.execute(
                "INSERT INTO application_events(kind,outcome,environment,duration_ms,timings) VALUES (%s,%s,%s,%s,%s)",
                (
                    kind,
                    outcome,
                    self.environment,
                    min(2**31 - 1, max(0, round(seconds * 1000))),
                    Jsonb(list(spans)[:1000]),
                ),
            )

    def summary(self):
        with self.database.connect() as connection:
            groups = list(
                connection.execute(
                    "SELECT kind,outcome,count(*) AS count,round(avg(duration_ms)) AS mean_ms FROM application_events WHERE environment=%s GROUP BY kind,outcome ORDER BY kind,outcome",
                    (self.environment,),
                )
            )
            counts = connection.execute(
                "SELECT count(*) AS variants,count(price_minor) AS priced,count(colour) AS colour_known,count(size) AS size_known,count(stock_quantity) AS stock_known FROM variants"
            ).fetchone()
            adds = connection.execute(
                "SELECT count(*) AS count FROM operation_receipts"
            ).fetchone()["count"]
        return {
            "environment": self.environment,
            "events": groups,
            "coverage": dict(counts),
            "committed_local_adds": adds,
            "popular_queries": "Not collected: raw query retention is disabled",
            "conversion": "Not measured: checkout is outside scope",
        }

    def cleanup(self, days=7):
        if type(days) is not int or not 1 <= days <= 30:
            raise ValueError("Retention must be 1–30 days")
        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM application_events WHERE occurred_at<%s",
                (datetime.now(UTC) - timedelta(days=days),),
            )
