CREATE SEQUENCE IF NOT EXISTS trades_id_seq START 1 OWNED BY trades.id;
ALTER TABLE trades ALTER COLUMN id SET DEFAULT nextval('trades_id_seq'::regclass);
