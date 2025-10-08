from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path("timing.db")


def init_db():
    """Create the SQLite database and table if they don’t exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                uri TEXT NOT NULL,
                duration REAL NOT NULL
            )
        """)
        conn.commit()


@app.route("/log", methods=["POST"])
def log_entry():
    """
    POST /log
    JSON body: {"uri": "<string>", "duration": <float>}
    Records the current timestamp, URI, and duration into SQLite.
    """
    data = request.get_json(force=True)

    uri = data.get("uri")
    duration = data.get("duration")

    if not uri or duration is None:
        return jsonify({"error": "Missing 'uri' or 'duration'"}), 400

    timestamp = datetime.utcnow().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO logs (timestamp, uri, duration) VALUES (?, ?, ?)",
            (timestamp, uri, duration),
        )
        conn.commit()

    return jsonify({"message": "Log saved", "timestamp": timestamp}), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
