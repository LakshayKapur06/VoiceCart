CREATE TABLE sessions (
    session_id uuid PRIMARY KEY,
    expires_at timestamptz NOT NULL,
    active_turn uuid,
    current_list_id uuid,
    mutation_version bigint NOT NULL DEFAULT 0 CHECK (mutation_version >= 0)
);
CREATE TABLE result_lists (
    list_id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    turn_id uuid NOT NULL,
    catalogue_revision text NOT NULL,
    offers jsonb NOT NULL CHECK (jsonb_typeof(offers)='array'),
    presented boolean NOT NULL DEFAULT false,
    expires_at timestamptz NOT NULL
);
CREATE TABLE cart_items (
    session_id uuid NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    variant_id text NOT NULL,
    quantity bigint NOT NULL CHECK (quantity > 0),
    PRIMARY KEY(session_id,variant_id)
);
CREATE TABLE commands (
    operation_id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    turn_id uuid NOT NULL,
    fingerprint text NOT NULL,
    payload jsonb NOT NULL,
    status text NOT NULL CHECK (status IN ('prepared','committed','rejected','cancelled')),
    failure_code text,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX one_prepared_operation ON commands(session_id) WHERE status='prepared';
CREATE TABLE operation_receipts (
    operation_id uuid PRIMARY KEY REFERENCES commands(operation_id) ON DELETE CASCADE,
    session_id uuid NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    turn_id uuid NOT NULL,
    fingerprint text NOT NULL,
    variant_id text NOT NULL,
    product_name text NOT NULL,
    added_quantity bigint NOT NULL CHECK (added_quantity > 0),
    resulting_quantity bigint NOT NULL CHECK (resulting_quantity >= added_quantity),
    unit_price_minor bigint NOT NULL CHECK (unit_price_minor >= 0),
    line_price_minor bigint NOT NULL CHECK (line_price_minor >= 0),
    currency text NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    catalogue_revision text NOT NULL,
    committed_at timestamptz NOT NULL DEFAULT now(),
    CHECK (line_price_minor = unit_price_minor * added_quantity)
);
CREATE FUNCTION prevent_receipt_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'Operation receipts are immutable';
END;
$$;
CREATE TRIGGER immutable_receipt BEFORE UPDATE ON operation_receipts FOR EACH ROW EXECUTE FUNCTION prevent_receipt_update();
