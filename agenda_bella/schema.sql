CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, login TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)), session_token TEXT,
 last_seen INTEGER, failures INTEGER NOT NULL DEFAULT 0, locked_until INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS clients (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS appointments (
 id INTEGER PRIMARY KEY, client_id INTEGER NOT NULL REFERENCES clients(id),
 user_id INTEGER NOT NULL REFERENCES users(id), service TEXT NOT NULL,
 start TEXT NOT NULL, end TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>=0),
 location TEXT NOT NULL CHECK(location IN ('fixo','domiciliar')), address TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL DEFAULT 'agendado' CHECK(status IN ('agendado','concluido','cancelado')),
 CHECK(end>start)
);
CREATE INDEX IF NOT EXISTS idx_appointments_start ON appointments(start);
CREATE TABLE IF NOT EXISTS blocks (
 id INTEGER PRIMARY KEY, start TEXT NOT NULL, end TEXT NOT NULL, reason TEXT NOT NULL, CHECK(end>start)
);
CREATE TABLE IF NOT EXISTS payments (
 id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL UNIQUE REFERENCES appointments(id),
 amount INTEGER NOT NULL CHECK(amount>=0), received_at TEXT NOT NULL
);
