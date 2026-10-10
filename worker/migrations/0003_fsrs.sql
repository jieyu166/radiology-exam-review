-- FSRS scheduler state (study-scheduler change): cards are last-write-wins by updated_at,
-- review logs are append-only (UNIQUE(user_id, client_id)), settings are last-write-wins.
-- attempts.source gains 'review' (ratings from the review queue). SQLite cannot alter a CHECK,
-- so the attempts table is rebuilt in place preserving ids and rows.

CREATE TABLE fsrs_cards (
  user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  question_id    TEXT    NOT NULL,
  due_at         INTEGER NOT NULL,
  stability      REAL    NOT NULL DEFAULT 0,
  difficulty     REAL    NOT NULL DEFAULT 0,
  elapsed_days   INTEGER NOT NULL DEFAULT 0,
  scheduled_days INTEGER NOT NULL DEFAULT 0,
  learning_steps INTEGER NOT NULL DEFAULT 0,
  reps           INTEGER NOT NULL DEFAULT 0,
  lapses         INTEGER NOT NULL DEFAULT 0,
  state          INTEGER NOT NULL DEFAULT 0 CHECK (state IN (0, 1, 2, 3)),
  last_review_at INTEGER,
  updated_at     INTEGER NOT NULL,
  PRIMARY KEY (user_id, question_id)
);
CREATE INDEX idx_fsrs_cards_user_due ON fsrs_cards (user_id, due_at);

CREATE TABLE fsrs_review_logs (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  client_id         TEXT    NOT NULL,
  question_id       TEXT    NOT NULL,
  rating            TEXT    NOT NULL CHECK (rating IN ('again', 'hard', 'good', 'easy')),
  state             INTEGER NOT NULL CHECK (state IN (0, 1, 2, 3)),   -- state before the rating
  due_at            INTEGER NOT NULL,
  stability         REAL    NOT NULL DEFAULT 0,
  difficulty        REAL    NOT NULL DEFAULT 0,
  elapsed_days      INTEGER NOT NULL DEFAULT 0,
  last_elapsed_days INTEGER NOT NULL DEFAULT 0,
  scheduled_days    INTEGER NOT NULL DEFAULT 0,
  learning_steps    INTEGER NOT NULL DEFAULT 0,
  reviewed_at       INTEGER NOT NULL,
  created_at        INTEGER NOT NULL,
  UNIQUE (user_id, client_id)
);
CREATE INDEX idx_fsrs_review_logs_user_time ON fsrs_review_logs (user_id, reviewed_at);

CREATE TABLE user_settings (
  user_id                  INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  new_per_day              INTEGER NOT NULL DEFAULT 20,
  day_start_hour           INTEGER NOT NULL DEFAULT 4,
  exam_seconds_per_question INTEGER NOT NULL DEFAULT 90,
  updated_at               INTEGER NOT NULL
);

-- Rebuild attempts with the widened source CHECK.
CREATE TABLE attempts_new (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  client_id     TEXT    NOT NULL,
  question_id   TEXT    NOT NULL,
  chosen        TEXT    CHECK (chosen IS NULL OR chosen IN ('A','B','C','D','E')),
  is_correct    INTEGER CHECK (is_correct IS NULL OR is_correct IN (0, 1)),
  source        TEXT    NOT NULL CHECK (source IN ('card', 'exam', 'review', 'legacy')),
  elapsed_ms    INTEGER CHECK (elapsed_ms IS NULL OR (elapsed_ms >= 0 AND elapsed_ms <= 1800000)),
  confidence    INTEGER CHECK (confidence IS NULL OR confidence IN (1, 2, 3)),
  source_sha256 TEXT,
  client_ts     INTEGER NOT NULL,
  created_at    INTEGER NOT NULL,
  UNIQUE (user_id, client_id)
);
INSERT INTO attempts_new (id, user_id, client_id, question_id, chosen, is_correct, source, elapsed_ms, confidence, source_sha256, client_ts, created_at)
  SELECT id, user_id, client_id, question_id, chosen, is_correct, source, elapsed_ms, confidence, source_sha256, client_ts, created_at FROM attempts;
DROP TABLE attempts;
ALTER TABLE attempts_new RENAME TO attempts;
CREATE INDEX idx_attempts_user_time ON attempts (user_id, created_at);
CREATE INDEX idx_attempts_user_question ON attempts (user_id, question_id, created_at);
