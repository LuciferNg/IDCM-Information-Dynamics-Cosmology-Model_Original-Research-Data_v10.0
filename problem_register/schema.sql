-- problem_register schema (v2)
-- Append-only lifecycle register for IDCM open problems.
-- Records ONLY lifecycle metadata: registration / ownership / closure /
-- negative result / post-hoc flag / progress timestamps.
-- NEVER results, NEVER derivation content.
--
-- register.jsonl  = system of record (append-only text, git-mergeable)
-- register.sqlite = generated query index (gitignored, fully rebuildable)
-- REGISTER.md     = generated human mirror (read-only)
--
-- KEY = pid:  'O213'      O-series problem
--             'bbn/he3'   problem inside a theme folder (no O number)

PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- One row per problem. title/keywords are an INDEX ENTRY, not content.
CREATE TABLE IF NOT EXISTS o_problem (
  pid         TEXT PRIMARY KEY,             -- 'O213' | 'bbn/he3'
  num         INTEGER,                      -- O number; NULL for theme problems
  slug        TEXT NOT NULL,                -- folder slug / theme path
  title       TEXT NOT NULL,                -- <= 120 chars, one line
  keywords    TEXT,                         -- <= 200 chars, for ownership lookup
  owner       TEXT,                         -- current owner (O### or theme name)
  state       TEXT NOT NULL DEFAULT 'registered',
                                            -- registered|open|partial|closed|merged|retracted|tombstone
  verdict     TEXT,                         -- closed|negative|partial|falsified (last)
  flags       TEXT,                         -- comma set, e.g. 'posthoc' (never overwrites verdict)
  created_ts  TEXT NOT NULL,
  backfilled  INTEGER NOT NULL DEFAULT 0,   -- 1 = seeded from legacy markdown
  state_source TEXT                         -- readme|problem_record|session_start|inferred|manual
);

CREATE INDEX IF NOT EXISTS idx_problem_num   ON o_problem(num);
CREATE INDEX IF NOT EXISTS idx_problem_state ON o_problem(state);

-- Append-only event log. Never UPDATE, never DELETE.
CREATE TABLE IF NOT EXISTS event (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  ts        TEXT    NOT NULL,               -- ISO8601 with local offset
  pid       TEXT,                           -- problem id; NULL = repo-level event
  num       INTEGER,                        -- derived from pid when O-series
  kind      TEXT    NOT NULL,               -- registered|assigned|progress|closed|reopened|
                                            -- merged|handed_off|retracted|tombstone|posthoc|note
  verdict   TEXT,                           -- closed|negative|partial|falsified
  owner     TEXT,                           -- for assigned / handed_off
  slug      TEXT,                           -- registration payload (replay source)
  title     TEXT,
  keywords  TEXT,
  state     TEXT,                           -- explicit state transition, if any
  state_source TEXT,                        -- readme|problem_record|session_start|inferred|manual
  target_pid TEXT,                          -- for merged / handed_off
  ref       TEXT,                           -- doc path/anchor (a POINTER, not content)
  note      TEXT,                           -- <= 200 chars
  session   TEXT,
  source    TEXT,                           -- cli | backfill:<path>
  prev_hash TEXT,                           -- tamper-evident chain
  hash      TEXT,
  -- 2026-10-24 結論迭代層（conclusion）
  -- 一文件可含多結論；多文件可支撐一結論；腳本 A 可解決問題 B
  pids      TEXT,                           -- JSON array: 結論歸屬問題（可多個）
  refs      TEXT,                           -- JSON array: 支撐文件/腳本（可多個）
  concl_hash TEXT,                          -- 結論 node id = sha256(claim)[:16]
  supersedes TEXT,                          -- JSON array: 被本結論取代嘅 concl_hash（DAG 邊）
  version   TEXT,                           -- 框架版本（v10.0 / v11.0）
  origin    TEXT                           -- 產生來源（pid/script/doc；可跨問題）
);

CREATE INDEX IF NOT EXISTS idx_event_pid  ON event(pid, id);
CREATE INDEX IF NOT EXISTS idx_event_ts   ON event(ts);
CREATE INDEX IF NOT EXISTS idx_event_kind ON event(kind);

-- Number allocation: reserved numbers that must never be reused.
CREATE TABLE IF NOT EXISTS reserved_num (
  num    INTEGER PRIMARY KEY,
  reason TEXT NOT NULL,
  ts     TEXT NOT NULL
);

-- Cross-theme / cross-era LABEL RESOLUTION.
-- A label as WRITTEN in a scope means a specific pid.
--   scope = 'global'  (README / O-series docs)
--         | '<theme>' (e.g. 'cmb_cold_spot' - its own internal numbering)
-- Rebuildable from events with kind='alias' (owner=scope, slug=label,
-- pid=resolved, note=note).  Never overrides the original text: the original
-- always wins, this only RECORDS what a stale label currently points at.
CREATE TABLE IF NOT EXISTS alias (
  scope TEXT NOT NULL,
  label TEXT NOT NULL,
  pid   TEXT NOT NULL,
  note  TEXT,
  ts    TEXT NOT NULL,
  PRIMARY KEY (scope, label)
);

-- One number, several directories.  RECORDED, never auto-resolved:
-- which one is canonical is the owner's call (原文贏).
-- Rebuildable from events with kind='collision'.
CREATE TABLE IF NOT EXISTS collision (
  num  INTEGER NOT NULL,
  dirs TEXT NOT NULL,           -- JSON list of directory names
  note TEXT,
  ts   TEXT NOT NULL,
  PRIMARY KEY (num, dirs)
);

