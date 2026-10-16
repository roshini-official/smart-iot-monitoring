
from datetime import datetime
import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)

DB_FILE = "waste_history.db"
BIN_HEIGHT_CM = 40

ALLOWED_BINS = {
    "Main Gate",
    "Canteen",
    "Library",
    "Parking Area",
    "Hostel",
}


def calculate_fill_level(distance_cm):
    return round(
        max(
            0,
            min(
                100,
                (BIN_HEIGHT_CM - distance_cm)
                / BIN_HEIGHT_CM * 100,
            ),
        ),
        1,
    )


def get_status(fill):
    if fill >= 90:
        return "Critical"
    if fill >= 80:
        return "Collection Required"
    if fill >= 65:
        return "Nearly Full"
    return "Normal"


def initialize_database():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                bin_name TEXT NOT NULL,
                distance_cm REAL NOT NULL,
                fill_level REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Smart Dustbin Sensor Receiver",
        "status": "running",
        "endpoint": "POST /sensor",
    })


@app.route("/sensor", methods=["POST"])
def receive_sensor_data():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({"error": "JSON body required"}), 400

    bin_name = payload.get("bin_name")
    distance = payload.get("distance_cm")

    if bin_name not in ALLOWED_BINS:
        return jsonify({
            "error": "Unknown bin_name",
            "allowed_bins": sorted(ALLOWED_BINS),
        }), 400

    try:
        distance = float(distance)
    except (TypeError, ValueError):
        return jsonify({
            "error": "distance_cm must be a number"
        }), 400

    # Reject impossible readings rather than treating them as real data.
    if not 2 <= distance <= BIN_HEIGHT_CM:
        return jsonify({
            "error": f"distance_cm must be between 2 and {BIN_HEIGHT_CM}"
        }), 400

    fill = calculate_fill_level(distance)
    status = get_status(fill)
    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        conn.execute("""
            INSERT INTO sensor_readings
                (timestamp, bin_name, distance_cm, fill_level, status)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, bin_name, distance, fill, status))

    return jsonify({
        "message": "Reading saved",
        "bin_name": bin_name,
        "distance_cm": distance,
        "fill_level": fill,
        "status": status,
        "timestamp": timestamp,
    }), 201


if __name__ == "__main__":
    initialize_database()

    # Keep this receiver on your trusted local network only.
    app.run(host="0.0.0.0", port=5000, debug=False)
