import os
import logging
from flask import Flask, jsonify
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)

# Read configuration from environment variables.
# Defaults are suitable only for local development / Docker Compose
# when the PostgreSQL service is named "database".
DB_HOST = os.getenv("DB_HOST", "database")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "securestack")
DB_USER = os.getenv("DB_USER", "securestack_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
app.logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def get_db_connection():
    """Open a short-lived PostgreSQL connection."""
    if not DB_PASSWORD:
        raise RuntimeError(
            "POSTGRES_PASSWORD environment variable is not configured"
        )

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=3,
    )


@app.get("/")
def index():
    return jsonify(
        service="SecureStack Backend",
        status="Online",
        endpoints=["/api/health", "/api/status"],
    )


@app.get("/api/health")
def health():
    # Liveness check: confirms that the Flask process is responding.
    return jsonify(status="Online", backend="Connected"), 200


@app.get("/api/status")
def status():
    # Readiness check: confirms PostgreSQL connectivity as well.
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]

        return jsonify(
            backend="Connected",
            database="Connected",
            database_version=version,
        ), 200

    except Exception:
        # Log the technical cause on the server; do not expose credentials
        # or internal exception details in the HTTP response.
        app.logger.exception("Database status check failed")
        return jsonify(
            backend="Connected",
            database="Disconnected",
            message="Database connection is unavailable.",
        ), 503


if __name__ == "__main__":
    # For local development only. For production, use a WSGI server
    # such as Gunicorn (for example: gunicorn -b 0.0.0.0:5000 backend:app).
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
