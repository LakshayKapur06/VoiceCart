CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE catalogue_state (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    revision text NOT NULL CHECK (length(revision) > 0),
    coverage text NOT NULL CHECK (coverage IN ('unknown','partial','complete')),
    populated boolean NOT NULL DEFAULT false,
    source text,
    valid_until timestamptz,
    generation text,
    dimensions integer CHECK (dimensions > 0 AND dimensions <= 4096),
    aliases jsonb NOT NULL DEFAULT '{}',
    published_at timestamptz NOT NULL DEFAULT now()
);
-- Metadata only. Migrations and normal startup NEVER seed product records.
INSERT INTO catalogue_state(singleton,revision,coverage) VALUES (true,'unpopulated','unknown');
CREATE TABLE products (
    product_id text PRIMARY KEY CHECK (length(btrim(product_id)) > 0),
    name text NOT NULL CHECK (length(btrim(name)) > 0),
    category text,
    model_number text,
    description text NOT NULL DEFAULT '',
    active boolean NOT NULL,
    CHECK (category IS NULL OR length(btrim(category)) > 0),
    CHECK (model_number IS NULL OR length(btrim(model_number)) > 0)
);
CREATE TABLE variants (
    variant_id text PRIMARY KEY CHECK (length(btrim(variant_id)) > 0),
    product_id text NOT NULL REFERENCES products(product_id),
    sku text UNIQUE,
    colour text,
    size text,
    price_minor bigint CHECK (price_minor >= 0),
    currency text CHECK (currency ~ '^[A-Z]{3}$'),
    available boolean,
    stock_quantity bigint CHECK (stock_quantity >= 0),
    price_freshness text NOT NULL CHECK (price_freshness IN ('unknown','stale','current')),
    active boolean NOT NULL,
    CHECK ((price_minor IS NULL) = (currency IS NULL)),
    CHECK (available IS DISTINCT FROM true OR stock_quantity IS DISTINCT FROM 0),
    CHECK (sku IS NULL OR length(btrim(sku)) > 0),
    CHECK (colour IS NULL OR length(btrim(colour)) > 0),
    CHECK (size IS NULL OR length(btrim(size)) > 0)
);
CREATE INDEX variants_product ON variants(product_id);
CREATE INDEX variants_price ON variants(currency,price_minor,variant_id);
CREATE TABLE variant_search (
    variant_id text PRIMARY KEY REFERENCES variants(variant_id) ON DELETE CASCADE,
    generation text,
    content_hash text NOT NULL,
    document text NOT NULL,
    lexical_document tsvector GENERATED ALWAYS AS (to_tsvector('simple',document)) STORED,
    embedding vector,
    CHECK ((embedding IS NULL) = (generation IS NULL)),
    CHECK (embedding IS NULL OR vector_dims(embedding) BETWEEN 1 AND 4096)
);
CREATE INDEX variant_search_lexical ON variant_search USING gin(lexical_document);
