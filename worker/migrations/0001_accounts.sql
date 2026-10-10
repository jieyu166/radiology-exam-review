-- Accounts: invite-only users, bearer sessions, login lockout.
-- Passwords are PBKDF2-HMAC-SHA256 PHC strings; tokens and invite codes are stored only as SHA-256 hex.

CREATE TABLE users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT    NOT NULL UNIQUE,            -- normalized lowercase, ^[a-z0-9][a-z0-9_.-]{2,31}$
  display_name  TEXT    NOT NULL DEFAULT '',
  password_hash TEXT    NOT NULL,                   -- $pbkdf2-sha256$i=<n>$<salt b64url>$<hash b64url>
  role          TEXT    NOT NULL DEFAULT 'member' CHECK (role IN ('member', 'admin')),
  created_at    INTEGER NOT NULL,
  disabled_at   INTEGER
);

CREATE TABLE invites (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  code_hash   TEXT    NOT NULL UNIQUE,              -- sha256 hex of the 24-char base32 code
  note        TEXT    NOT NULL DEFAULT '',
  created_by  INTEGER REFERENCES users(id),
  created_at  INTEGER NOT NULL,
  expires_at  INTEGER NOT NULL,
  used_by     INTEGER REFERENCES users(id),
  used_at     INTEGER,
  revoked_at  INTEGER
);

CREATE TABLE sessions (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash   TEXT    NOT NULL UNIQUE,             -- sha256 hex of the bearer token
  created_at   INTEGER NOT NULL,
  expires_at   INTEGER NOT NULL,
  last_used_at INTEGER,
  user_agent   TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX idx_sessions_user ON sessions (user_id);
CREATE INDEX idx_sessions_expires ON sessions (expires_at);

CREATE TABLE login_attempts (
  username     TEXT    PRIMARY KEY,
  failed_count INTEGER NOT NULL DEFAULT 0,
  locked_until INTEGER,
  updated_at   INTEGER NOT NULL
);
