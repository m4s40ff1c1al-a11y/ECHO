import os, sqlite3, pathlib, json, time
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "data/echo.db")
pathlib.Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS owner (
          id INTEGER PRIMARY KEY CHECK(id=1), username TEXT NOT NULL,
          password_hash TEXT NOT NULL, created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS memories (
          id INTEGER PRIMARY KEY AUTOINCREMENT, layer TEXT NOT NULL,
          encrypted_content TEXT NOT NULL, created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
          detail TEXT NOT NULL, created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS proposals (
          id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
          description TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'proposed',
          created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ai_projects (
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          description TEXT NOT NULL, personality TEXT NOT NULL, model TEXT NOT NULL,
          capabilities_json TEXT NOT NULL, created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS conversations (
          id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL,
          content TEXT NOT NULL, created_at INTEGER NOT NULL
        );
        """)

def log_event(event, detail=""):
    with db() as c:
        c.execute("INSERT INTO events(event,detail,created_at) VALUES(?,?,?)",
                  (event, detail[:500], int(time.time())))
