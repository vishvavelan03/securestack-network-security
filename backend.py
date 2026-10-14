import os
import logging

from flask import Flask, jsonify
from dotenv import load_dotenv
import psycopg2

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "service": "SecureStack API",
        "status": "Online"
    })


@app.route("/api/health")
def health():
    return jsonify({
        "status": "Online",
        "backend": "Connected"
    }), 200


@app.route("/api/status")
def status():
    connection = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "securestack"),
            user=os.getenv("DB_USER", "securestack_user"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            connect_timeout=3
        )

        return jsonify({
            "backend": "Connected",
            "database": "Connected",
            "status": "Online"
        }), 200

    except Exception:
        app.logger.exception("Database connection failed")
        return jsonify({
            "backend": "Connected",
            "database": "Disconnected",
            "message": "Check PostgreSQL configuration."
        }), 503

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False
    )
