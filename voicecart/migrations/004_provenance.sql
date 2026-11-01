CREATE TABLE product_metadata (
 product_id text PRIMARY KEY REFERENCES products(product_id) ON DELETE CASCADE,
 payload jsonb NOT NULL CHECK (jsonb_typeof(payload)='object')
);
CREATE INDEX product_metadata_brand ON product_metadata ((payload->>'brand'));
CREATE TABLE import_history (
 import_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 revision text NOT NULL,
 source text NOT NULL,
 product_count integer NOT NULL,
 variant_count integer NOT NULL,
 published_at timestamptz NOT NULL DEFAULT now()
);
