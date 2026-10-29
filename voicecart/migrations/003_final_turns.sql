-- A final turn is accepted once by the application, including after a restart.
ALTER TABLE sessions ADD COLUMN accepted_turn uuid;
