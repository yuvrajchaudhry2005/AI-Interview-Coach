import hashlib
import hmac
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone


DATABASE_PATH = os.environ.get(
    "AUTH_DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "interview_coach.db"),
)
HASH_ITERATIONS = 310_000


@contextmanager
def _connect():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()


def init_database():
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                interview_type TEXT NOT NULL,
                score REAL NOT NULL,
                question_count INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )


def _hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, HASH_ITERATIONS
    )
    return f"pbkdf2_sha256${HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def _verify_password(password, stored_hash):
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (TypeError, ValueError):
        return False


def create_user(full_name, email, password):
    normalized_email = email.strip().lower()
    with _connect() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO users (full_name, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    full_name.strip(),
                    normalized_email,
                    _hash_password(password),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        except sqlite3.IntegrityError:
            return None
        return {"id": cursor.lastrowid, "full_name": full_name.strip(), "email": normalized_email}


def authenticate_user(email, password):
    normalized_email = email.strip().lower()
    with _connect() as connection:
        user = connection.execute(
            "SELECT id, full_name, email, password_hash FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()
    if not user or not _verify_password(password, user["password_hash"]):
        return None
    return {"id": user["id"], "full_name": user["full_name"], "email": user["email"]}


def save_interview_history(user_id, session_id, role, interview_type, score, question_count):
    with _connect() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO interview_history
                (user_id, session_id, role, interview_type, score, question_count, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                session_id,
                role,
                interview_type,
                score,
                question_count,
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def get_interview_history(user_id):
    with _connect() as connection:
        return connection.execute(
            """
            SELECT role, interview_type, score, question_count, completed_at
            FROM interview_history
            WHERE user_id = ?
            ORDER BY completed_at DESC
            """,
            (user_id,),
        ).fetchall()


def delete_user(user_id):
    with _connect() as connection:
        connection.execute("DELETE FROM interview_history WHERE user_id = ?", (user_id,))
        connection.execute("DELETE FROM users WHERE id = ?", (user_id,))