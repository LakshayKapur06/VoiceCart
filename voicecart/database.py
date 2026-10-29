"""One PostgreSQL authority: versioned migrations and atomic full publications."""

from __future__ import annotations

import hashlib
import ipaddress
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import resources
from typing import Any

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from voicecart.catalogue import InMemoryCatalogue
from voicecart.domain import (
    CatalogueItem,
    Coverage,
    Freshness,
    Money,
    Product,
    ProductId,
    Variant,
    VariantId,
)
from voicecart.embeddings import OllamaEncoder, vector_literal
from voicecart.ingestion import CatalogueImport, content_hash, search_document


class DatabaseUnavailable(RuntimeError):
    pass


class PublicationConflict(ValueError):
    pass


@dataclass(frozen=True)
class Snapshot:
    state: dict[str, Any]
    catalogue: InMemoryCatalogue
    items: tuple[CatalogueItem, ...]


def parse_local_dsn(dsn: str) -> dict[str, str]:
    try:
        config = {
            key: str(value)
            for key, value in conninfo_to_dict(dsn).items()
            if value is not None
        }
        host = config.get("host", "")
        if "," in host or os.environ.get("PGHOSTADDR") or os.environ.get("PGSERVICE"):
            raise ValueError("Ambiguous PostgreSQL host or service configuration")
        config["host"] = host or "127.0.0.1"
        local = not host or host.startswith("/") or host == "localhost"
        if not local:
            local = ipaddress.ip_address(host).is_loopback
        if not local or "hostaddr" in config or config.get("service"):
            raise ValueError("Only a local PostgreSQL database is supported")
        if not config.get("dbname"):
            raise ValueError("An explicit database name is required")
        return config
    except (psycopg.Error, ValueError) as exc:
        raise ValueError("Configure an explicit local PostgreSQL DSN") from exc


class Database:
    def __init__(self, dsn: str):
        self._config = parse_local_dsn(dsn)

    @contextmanager
    def connect(self):
        try:
            parameters: dict[str, Any] = dict(self._config)
            parameters.update(
                connect_timeout=5,
                options="-c search_path=public -c statement_timeout=10000 -c lock_timeout=3000",
            )
            with psycopg.connect(**parameters, row_factory=dict_row) as connection:
                yield connection
        except psycopg.OperationalError as exc:
            raise DatabaseUnavailable(
                "Local database unavailable; operation outcome may require reconciliation"
            ) from exc

    def migrate(self) -> list[str]:
        applied = []
        with self.connect() as connection:
            connection.execute("SELECT pg_advisory_xact_lock(1448231761)")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version text PRIMARY KEY, sha256 text NOT NULL)"
            )
            migrations = resources.files("voicecart").joinpath("migrations")
            for path in sorted(migrations.iterdir(), key=lambda value: value.name):
                if not path.name.endswith(".sql"):
                    continue
                source = path.read_text(encoding="utf-8")
                digest = hashlib.sha256(source.encode()).hexdigest()
                existing = connection.execute(
                    "SELECT sha256 FROM schema_migrations WHERE version=%s",
                    (path.name,),
                ).fetchone()
                if existing:
                    if existing["sha256"] != digest:
                        raise PublicationConflict("Applied migration checksum differs")
                    continue
                connection.execute(source)
                connection.execute(
                    "INSERT INTO schema_migrations VALUES (%s,%s)", (path.name, digest)
                )
                applied.append(path.name)
        return applied

    def check_ready(self) -> None:
        with self.connect() as connection:
            connection.execute(
                "SELECT revision FROM catalogue_state WHERE singleton=true"
            ).fetchone()
            extension = connection.execute(
                "SELECT extversion FROM pg_extension WHERE extname='vector'"
            ).fetchone()
            if not extension:
                raise DatabaseUnavailable(
                    "pgvector extension is unavailable; run explicit migrations"
                )

    def inspect(self) -> dict:
        with self.connect() as connection:
            connection.execute(
                "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
            )
            state = dict(
                connection.execute(
                    "SELECT * FROM catalogue_state WHERE singleton=true"
                ).fetchone()
            )
            state["product_count"] = connection.execute(
                "SELECT count(*) AS n FROM products"
            ).fetchone()["n"]
            state["variant_count"] = connection.execute(
                "SELECT count(*) AS n FROM variants"
            ).fetchone()["n"]
            state["search_count"] = connection.execute(
                "SELECT count(*) AS n FROM variant_search"
            ).fetchone()["n"]
            return state

    def snapshot_in(self, connection) -> Snapshot:
        state = dict(
            connection.execute(
                "SELECT * FROM catalogue_state WHERE singleton=true"
            ).fetchone()
        )
        expired = state["valid_until"] is None or state["valid_until"] <= datetime.now(
            UTC
        )
        products = {
            product.product_id: product
            for product in (
                Product(**row) for row in connection.execute("SELECT * FROM products")
            )
        }
        variants = []
        for row in connection.execute(
            "SELECT to_jsonb(p) AS product,to_jsonb(v) AS variant FROM variants v JOIN products p USING(product_id) ORDER BY v.variant_id"
        ):
            product = Product(**row["product"])
            products[product.product_id] = product
            fields = row["variant"]
            price = (
                Money(fields.pop("price_minor"), fields.pop("currency"))
                if fields["price_minor"] is not None
                else None
            )
            fields.pop("price_minor", None)
            fields.pop("currency", None)
            fields["variant_id"] = VariantId(fields["variant_id"])
            fields["product_id"] = ProductId(fields["product_id"])
            fields["price_freshness"] = (
                Freshness.STALE if expired else Freshness(fields["price_freshness"])
            )
            if expired:
                fields["available"] = None
            variants.append(Variant(price=price, **fields))
        catalogue = InMemoryCatalogue(
            products.values(),
            variants,
            revision=state["revision"],
            coverage=Coverage(state["coverage"]),
        )
        items = tuple(CatalogueItem(products[v.product_id], v) for v in variants)
        return Snapshot(state, catalogue, items)

    def snapshot(self) -> Snapshot:
        with self.connect() as connection:
            connection.execute(
                "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
            )
            return self.snapshot_in(connection)

    def vocabulary(self) -> dict[str, dict[str, str]]:
        snapshot = self.snapshot()
        result: dict[str, dict[str, str]] = {"category": {}, "colour": {}, "size": {}}
        for item in snapshot.items:
            for name, value in (
                ("category", item.product.category),
                ("colour", item.variant.colour),
                ("size", item.variant.size),
            ):
                if value:
                    result[name][value.casefold()] = value
        for name, aliases in snapshot.state["aliases"].items():
            result[name].update(aliases)
        return result

    def publish(
        self, bundle: CatalogueImport, *, encoder: OllamaEncoder | None = None
    ) -> str:
        if not isinstance(bundle, CatalogueImport):
            raise TypeError("A validated catalogue import is required")
        InMemoryCatalogue(
            bundle.products,
            bundle.variants,
            revision=bundle.revision,
            coverage=bundle.coverage,
        )
        parents = {product.product_id: product for product in bundle.products}
        documents = [
            search_document(parents[variant.product_id], variant)
            for variant in bundle.variants
        ]
        vectors: list[tuple[float, ...] | None] = [None] * len(documents)
        if encoder is not None:
            for offset in range(0, len(documents), 32):
                vectors[offset : offset + 32] = encoder.encode(
                    documents[offset : offset + 32]
                )
        generation = encoder.spec.generation if encoder else None
        dimensions = encoder.spec.dimensions if encoder else None
        # Model work is complete before any write locks or transaction starts.
        with self.connect() as connection:
            state = connection.execute(
                "SELECT revision FROM catalogue_state WHERE singleton=true FOR UPDATE"
            ).fetchone()
            if state["revision"] != bundle.previous_revision:
                raise PublicationConflict(
                    "Publication revision changed; validate a new full snapshot"
                )
            if bundle.valid_until <= datetime.now(UTC):
                raise PublicationConflict("Catalogue source expired during preparation")
            connection.execute("DELETE FROM variant_search")
            connection.execute("DELETE FROM variants")
            connection.execute("DELETE FROM products")
            with connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO products(product_id,name,category,model_number,description,active) VALUES (%s,%s,%s,%s,%s,%s)",
                    [
                        (
                            p.product_id,
                            p.name,
                            p.category,
                            p.model_number,
                            p.description,
                            p.active,
                        )
                        for p in bundle.products
                    ],
                )
                cursor.executemany(
                    "INSERT INTO variants(variant_id,product_id,sku,colour,size,price_minor,currency,available,stock_quantity,price_freshness,active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [
                        (
                            v.variant_id,
                            v.product_id,
                            v.sku,
                            v.colour,
                            v.size,
                            v.price.minor_units if v.price else None,
                            v.price.currency if v.price else None,
                            v.available,
                            v.stock_quantity,
                            v.price_freshness.value,
                            v.active,
                        )
                        for v in bundle.variants
                    ],
                )
                cursor.executemany(
                    "INSERT INTO variant_search(variant_id,generation,content_hash,document,embedding) VALUES (%s,%s,%s,%s,%s::vector)",
                    [
                        (
                            v.variant_id,
                            generation,
                            content_hash(document),
                            document,
                            vector_literal(vector) if vector is not None else None,
                        )
                        for v, document, vector in zip(
                            bundle.variants, documents, vectors, strict=True
                        )
                    ],
                )
            connection.execute(
                "UPDATE catalogue_state SET revision=%s,coverage=%s,populated=true,source=%s,valid_until=%s,generation=%s,dimensions=%s,aliases=%s,published_at=now() WHERE singleton=true",
                (
                    bundle.revision,
                    bundle.coverage.value,
                    bundle.source,
                    bundle.valid_until,
                    generation,
                    dimensions,
                    Jsonb(bundle.aliases),
                ),
            )
        return bundle.revision
