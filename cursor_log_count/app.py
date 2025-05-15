import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, Blueprint, request, jsonify, redirect, url_for
from .countlog import count_log

# Create the blueprint
app = Blueprint("cursor_log_count", __name__, template_folder="templates", url_prefix="/cursor_log_count")
app.html_name = "Cursor Log Count"
app.html_creator = "איתמר"
app.html_link = "https://www.facebook.com/itamar.ho"  
app.html_img = "/static/itamar.ho.jpg"  

# Get the directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'count_log_history.db')

# Create the DB table if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS log_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        content TEXT,
        filename TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Initialize the database on import
init_db()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('cursor_log_count/templates/index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if the file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # If no file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Read the file content
    content = file.read().decode('utf-8')
    filename = file.filename
    
    # Save to database
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO log_entries (timestamp, content, filename) VALUES (?, ?, ?)',
        (timestamp, content, filename)
    )
    conn.commit()
    conn.close()
    
    # Analyze the content
    result = count_log(content)
    
    # Return the analysis result
    return jsonify(result)

@app.route('/admin')
def admin():
    # Get all log entries from the database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, filename FROM log_entries ORDER BY timestamp DESC')
    entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('admin.html', entries=entries)

@app.route('/admin/view/<int:entry_id>')
def view_entry(entry_id):
    # Get specific log entry content
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM log_entries WHERE id = ?', (entry_id,))
    row = cursor.fetchone()
    entry = dict(row) if row else None
    conn.close()
    
    if not entry:
        return "Entry not found", 404
    
    # Analyze the content
    result = count_log(entry['content'])
    
    return render_template('view_entry.html', entry=entry, analysis=result)

if __name__ == '__main__':
    # Consider using a different port if 5001 is taken or for separation
    app.run(debug=True, host='0.0.0.0', port=5002)