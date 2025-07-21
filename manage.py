from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import os
from flask import send_from_directory

app = Flask(__name__)
OUTPUT_DIR = "out_put"


# Giao diện chính KHÔNG preview
TEMPLATE_INDEX = """
<!doctype html>
<title>Detection Log Viewer</title>
<h2>🗂️ Detection Log Dashboard</h2>

<form method="get">
    <label>Date (YYYY-MM-DD):</label>
    <input name="date" type="text" value="{{date}}">
    <label>Min Motorbike:</label>
    <input name="min_motor" type="number" value="{{min_motor}}">
    <label>Min Car:</label>
    <input name="min_car" type="number" value="{{min_car}}">
    <button type="submit">Filter</button>
</form>

<table border=1 cellpadding=5>
<tr>
<th>ID</th><th>Input</th><th>Output</th><th>Time</th><th>Actions</th>
</tr>
{% for row in rows %}
<tr>
<td>{{row[0]}}</td>
<td>{{row[1]}}</td>
<td>{{row[2]}}</td>
<td>{{row[3]}}</td>
<td>
    <a href="/view/{{row[0]}}">View Details</a> |
    <a href="/delete/{{row[0]}}" onclick="return confirm('Delete log?')">Delete</a>
</td>
</tr>
{% endfor %}
</table>
"""

# Giao diện xem chi tiết
TEMPLATE_VIEW = """
<!doctype html>
<title>View Log Detail</title>
<div style="border:1px solid #ddd; padding:20px; border-radius:8px; max-width:400px; background:#f9f9f9;">
  <h3>📄 Log Details</h3>
  <ul style="list-style:none; padding:0;">
    <li><b>ID:</b> {{row[0]}}</li>
    <li><b>Input File:</b> {{row[1]}}</li>
    <li><b>Output File:</b> {{row[2]}}</li>
    <li><b>Time:</b> {{row[3]}}</li>
    <li><b>Motorbike:</b> {{row[4]}}</li>
    <li><b>Car:</b> {{row[5]}}</li>
  </ul>
</div>


<h3>📸 Output Preview</h3>
{% if row[2].endswith(".jpg") %}
  <img src="{{ url_for('file', filename=row[2] | basename) }}" width="500">
{% elif row[2].endswith(".mp4") %}
  <video width="640" controls>
    <source src="{{ url_for('file', filename=row[2] | basename) }}" type="video/mp4">
  </video>
{% endif %}
<br>
<a href="{{ url_for('file', filename=row[2] | basename) }}" download>Download Output</a> |
<a href="/">⬅ Back to Dashboard</a>

"""

@app.route("/", methods=["GET"])
def index():
    date = request.args.get("date", "")
    min_motor = request.args.get("min_motor", "0")
    min_car = request.args.get("min_car", "0")

    conn = sqlite3.connect("detect_logs.db")
    c = conn.cursor()

    query = "SELECT * FROM detection_logs WHERE 1=1"
    params = []

    if date:
        query += " AND timestamp LIKE ?"
        params.append(f"{date}%")
    if min_motor:
        query += " AND num_motor >= ?"
        params.append(int(min_motor))
    if min_car:
        query += " AND num_car >= ?"
        params.append(int(min_car))

    query += " ORDER BY timestamp DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    return render_template_string(
        TEMPLATE_INDEX,
        rows=rows,
        date=date,
        min_motor=min_motor,
        min_car=min_car
    )
@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path)

@app.route("/view/<int:log_id>")
def view(log_id):
    conn = sqlite3.connect("detect_logs.db")
    c = conn.cursor()
    c.execute("SELECT * FROM detection_logs WHERE id=?", (log_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return "Log not found", 404
    return render_template_string(TEMPLATE_VIEW, row=row)

@app.route("/file/<path:filename>")
def file(filename):
    return send_from_directory(OUTPUT_DIR, os.path.basename(filename))

@app.route("/delete/<int:log_id>")
def delete(log_id):
    conn = sqlite3.connect("detect_logs.db")
    c = conn.cursor()
    c.execute("SELECT output_file FROM detection_logs WHERE id=?", (log_id,))
    row = c.fetchone()
    if row:
        file_to_delete = row[0]
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
    c.execute("DELETE FROM detection_logs WHERE id=?", (log_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
