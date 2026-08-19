from flask import Flask, jsonify, send_from_directory, render_template
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.storage import EventDatabase

app = Flask(__name__)

# Config paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, 'logs', 'smart_desk.db')
SNAPSHOT_DIR = os.path.join(BASE_DIR, 'outputs', 'snapshots')

db = EventDatabase(DB_FILE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    events = db.get_recent_events(20)
    return jsonify(events)

@app.route('/snapshots/<filename>')
def get_snapshot(filename):
    return send_from_directory(SNAPSHOT_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
