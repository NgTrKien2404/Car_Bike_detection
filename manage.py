from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect("detect_logs.db")
    c = conn.cursor()
    c.execute("SELECT * FROM detection_logs ORDER BY timestamp DESC")
    logs = c.fetchall()
    conn.close()

    html = """
    <h2>Detection Logs</h2>
    <table border="1">
        <tr><th>ID</th><th>Input</th><th>Output</th><th>Time</th><th>Motorbike</th><th>Car</th></tr>
        {% for row in logs %}
        <tr>
            <td>{{row[0]}}</td>
            <td>{{row[1]}}</td>
            <td>{{row[2]}}</td>
            <td>{{row[3]}}</td>
            <td>{{row[4]}}</td>
            <td>{{row[5]}}</td>
        </tr>
        {% endfor %}
    </table>
    """
    return render_template_string(html, logs=logs)

if __name__ == "__main__":
    app.run(debug=True)
