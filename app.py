from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app, origins=["https://escriptorium.inria.fr"])
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


@app.cli.command("export-csv")
def export_csv():
    """
    Export all logs from the SQLite database to 'logs_export.csv'.
    Usage: flask export-csv
    """
    output_file = Path("logs_export.csv")
    with sqlite3.connect(DB_PATH) as conn, open(output_file, "w", newline="") as f:
        cursor = conn.execute("SELECT id, timestamp, uri, duration FROM logs ORDER BY id ASC")
        writer = csv.writer(f)
        writer.writerow([col[0] for col in cursor.description])  # header
        writer.writerows(cursor.fetchall())

    print(f"✅ Exported logs to {output_file.resolve()}")
    

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
