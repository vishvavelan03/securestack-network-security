import os
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "database")
DB_NAME = os.getenv("DB_NAME", "securestack")
DB_USER = os.getenv("DB_USER", "securestack_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=3,
    )


@app.get("/api/health")
def health():
    return jsonify(status="Online", backend="Connected")


@app.get("/api/status")
def status():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
        return jsonify(
            backend="Connected",
            database="Connected",
            database_version=version,
        )
    except Exception:
        app.logger.exception("Database status check failed")
        return jsonify(backend="Connected", database="Disconnected"), 503


if __name__ == "__main__":
    # Development server for this educational demo only.
    app.run(host="0.0.0.0", port=5000)
