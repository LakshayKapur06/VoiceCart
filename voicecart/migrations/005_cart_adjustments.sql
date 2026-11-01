CREATE TABLE cart_adjustments (
 operation_id uuid PRIMARY KEY,
 session_id uuid NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
 fingerprint text NOT NULL,
 receipt jsonb NOT NULL,
 committed_at timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER immutable_adjustment BEFORE UPDATE ON cart_adjustments FOR EACH ROW EXECUTE FUNCTION prevent_receipt_update();
