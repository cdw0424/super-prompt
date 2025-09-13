PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA temp_store=MEMORY;
PRAGMA busy_timeout=5000;

CREATE TABLE IF NOT EXISTS project (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  name       TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS memory (
  id          INTEGER PRIMARY KEY,
  project_id  INTEGER NOT NULL REFERENCES project(id),
  kind        TEXT NOT NULL,
  source      TEXT,
  author      TEXT,
  title       TEXT,
  body        TEXT NOT NULL,
  tags        TEXT,
  tokens      INTEGER NOT NULL DEFAULT 0,
  importance  REAL    NOT NULL DEFAULT 0.0,
  pinned      INTEGER NOT NULL DEFAULT 0,
  created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT,
  expires_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_memory_project_created ON memory(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_expiry           ON memory(expires_at);

-- FTS5 virtual table and triggers
CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
  title, body, tags, content='memory', content_rowid='id',
  tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON memory BEGIN
  INSERT INTO memory_fts(rowid, title, body, tags)
  VALUES (new.id, new.title, new.body, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS memory_ad AFTER DELETE ON memory BEGIN
  INSERT INTO memory_fts(memory_fts, rowid, title, body, tags)
  VALUES('delete', old.id, old.title, old.body, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS memory_au AFTER UPDATE ON memory BEGIN
  INSERT INTO memory_fts(memory_fts, rowid, title, body, tags)
  VALUES('delete', old.id, old.title, old.body, old.tags);
  INSERT INTO memory_fts(rowid, title, body, tags)
  VALUES (new.id, new.title, new.body, new.tags);
END;

-- Embedding storage (engine agnostic)
CREATE TABLE IF NOT EXISTS embedding (
  memory_id INTEGER PRIMARY KEY REFERENCES memory(id) ON DELETE CASCADE,
  dim       INTEGER NOT NULL,
  vector    BLOB    NOT NULL
);

-- Optional vector index examples (choose one and adjust per extension manual)
-- sqlite-vss
-- CREATE VIRTUAL TABLE embedding_idx USING vss0(embedding(1536));
-- INSERT INTO embedding_idx(rowid, embedding) SELECT memory_id, vector FROM embedding;

-- sqlite-vec
-- CREATE VIRTUAL TABLE embedding_idx USING vec0(embedding float[1536]);
-- INSERT INTO embedding_idx(rowid, embedding) SELECT memory_id, vector FROM embedding;

