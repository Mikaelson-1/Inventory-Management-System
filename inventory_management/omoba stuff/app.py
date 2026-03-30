# app.py
from flask import Flask, render_template, jsonify, Response
import os, sqlite3, time, json
import pandas as pd

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "traffic.db")
TABLE = "weather"

def get_latest_per_city() -> pd.DataFrame:
    with sqlite3.connect(DB_NAME) as conn:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {TABLE}", conn)
        except Exception as e:
            print("DB READ ERROR:", e)
            return pd.DataFrame(columns=["city","temperature","rain_chance","timestamp"])

    if df.empty:
        return df

    # aliasing in case your columns differ (adjust candidates if needed)
    def find(cols, *cands):
        low = {c.lower(): c for c in cols}
        for cand in cands:
            if cand.lower() in low: return low[cand.lower()]
        return None

    city_col = find(df.columns, "city", "location", "town")
    temp_col = find(df.columns, "temperature", "temp", "temp_c")
    rain_col = find(df.columns, "rain_chance", "rain", "precip", "pop", "rain_probability")
    ts_col   = find(df.columns, "timestamp", "time", "created_at", "updated_at", "datetime", "ts")

    need = []
    if not city_col: need.append("city")
    if not temp_col: need.append("temperature")
    if not rain_col: need.append("rain_chance")
    if not ts_col:   need.append("timestamp")
    if need:
        print("MISSING COLUMNS:", need, "available:", list(df.columns))
        return pd.DataFrame(columns=["city","temperature","rain_chance","timestamp"])

    df = df.rename(columns={
        city_col: "city",
        temp_col: "temperature",
        rain_col: "rain_chance",
        ts_col:   "timestamp"
    })

    # keep newest per city
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values(["city", "timestamp"], ascending=[True, False])
    latest = df.drop_duplicates(subset=["city"], keep="first").reset_index(drop=True)
    return latest

def predict_congestion(rain_chance: float) -> str:
    try:
        rc = float(rain_chance)
    except:
        return "Unknown"
    if rc >= 70: return "High"
    if rc >= 40: return "Moderate"
    return "Low"

@app.route("/")
def dashboard():
    # just render the page; the browser subscribes to /stream
    return render_template("dashboard.html")

@app.route("/data")
def data_once():
    """Optional: one-shot JSON (useful for testing)."""
    latest = get_latest_per_city()
    if latest.empty:
        return jsonify([])
    latest["congestion_level"] = latest["rain_chance"].apply(predict_congestion)
    for col in ("rain_chance","temperature"):
        if col in latest and pd.api.types.is_float_dtype(latest[col]):
            latest[col] = latest[col].round(1)
    if "timestamp" in latest and pd.api.types.is_datetime64_any_dtype(latest["timestamp"]):
        latest["timestamp"] = latest["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(latest.to_dict(orient="records"))

@app.route("/stream")
def stream():
    """SSE stream: pushes new data every 4 seconds."""
    def event_stream():
        # avoid duplicate streaming in debug reloader
        while True:
            latest = get_latest_per_city()
            if latest.empty:
                payload = []
            else:
                latest["congestion_level"] = latest["rain_chance"].apply(predict_congestion)
                for col in ("rain_chance","temperature"):
                    if col in latest and pd.api.types.is_float_dtype(latest[col]):
                        latest[col] = latest[col].round(1)
                if "timestamp" in latest and pd.api.types.is_datetime64_any_dtype(latest["timestamp"]):
                    latest["timestamp"] = latest["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
                payload = latest.to_dict(orient="records")

            # SSE format requires: data: ...\n\n
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(4)  # push interval

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        # Allow CORS if you view from another host:
        # "Access-Control-Allow-Origin": "*",
    }
    return Response(event_stream(), headers=headers)


import sqlite3
import random
import time
from datetime import datetime

DB_NAME = "traffic.db"  # Make sure this is the same file Flask uses

def randomize_rain_chance():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    while True:
        cursor.execute("SELECT city FROM weather")
        cities = cursor.fetchall()
        
        for (city,) in cities:
            new_rain_chance = random.randint(0, 100)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE weather
                SET rain_chance = ?, timestamp = ?
                WHERE city = ?
            """, (new_rain_chance, now, city))
        
        conn.commit()
        print(f"Updated rain chances at {datetime.now()}")
        
        time.sleep(4)

if __name__ == "__main__":
    # use_reloader=False so /stream doesn’t run twice in dev
    app.run(debug=True, threaded=True, use_reloader=False)
