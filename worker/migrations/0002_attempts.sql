-- Study progress: append-only attempt events, last-write-wins bookmarks, append-only exam results.
-- client_id is generated on the client (UUID or deterministic legacy:<qid>:<ts>); UNIQUE(user_id, client_id)
-- makes every upload idempotent via INSERT OR IGNORE. attempts rows are never updated or deleted by the API.

CREATE TABLE attempts (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  client_id     TEXT    NOT NULL,
  question_id   TEXT    NOT NULL,
  chosen        TEXT    CHECK (chosen IS NULL OR chosen IN ('A','B','C','D','E')),
  is_correct    INTEGER CHECK (is_correct IS NULL OR is_correct IN (0, 1)),
  source        TEXT    NOT NULL CHECK (source IN ('card', 'exam', 'legacy')),
  elapsed_ms    INTEGER CHECK (elapsed_ms IS NULL OR (elapsed_ms >= 0 AND elapsed_ms <= 1800000)),
  confidence    INTEGER CHECK (confidence IS NULL OR confidence IN (1, 2, 3)),
  source_sha256 TEXT,
  client_ts     INTEGER NOT NULL,
  created_at    INTEGER NOT NULL,
  UNIQUE (user_id, client_id)
);
CREATE INDEX idx_attempts_user_time ON attempts (user_id, created_at);
CREATE INDEX idx_attempts_user_question ON attempts (user_id, question_id, created_at);

CREATE TABLE bookmarks (
  user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  question_id TEXT    NOT NULL,
  starred     INTEGER NOT NULL CHECK (starred IN (0, 1)),
  updated_at  INTEGER NOT NULL,
  PRIMARY KEY (user_id, question_id)
);

CREATE TABLE exam_results (
  id                       INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id                  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  client_id                TEXT    NOT NULL,
  total                    INTEGER NOT NULL,
  correct                  INTEGER NOT NULL,
  wrong                    INTEGER NOT NULL,
  skipped                  INTEGER NOT NULL,
  pct                      INTEGER NOT NULL,
  wrong_ids                TEXT    NOT NULL DEFAULT '[]',   -- JSON array of question ids
  source_sha256_by_question TEXT   NOT NULL DEFAULT '{}',   -- JSON object
  client_ts                INTEGER NOT NULL,
  created_at               INTEGER NOT NULL,
  UNIQUE (user_id, client_id)
);
CREATE INDEX idx_exam_results_user_time ON exam_results (user_id, created_at);
