from flask import Flask, render_template, Response
import sqlite3
import cv2

app = Flask(__name__)

# ---------- Database ----------
def save_alert(alert_type, status):
    conn = sqlite3.connect("campus_safety.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO alerts (alert_type, status) VALUES (?, ?)",
        (alert_type, status)
    )

    conn.commit()
    conn.close()


# ---------- Camera ----------
camera = None

def generate_frames():
    if camera is None:
        return

    while True:
        success, frame = camera.read()

        if not success:
            break

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/camera")
def camera_page():
    return render_template("camera.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/sos")
def sos():
    save_alert("Emergency SOS", "Active")
    return render_template("sos.html")


@app.route("/alerts")
def alerts():
    conn = sqlite3.connect("campus_safety.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts")
    alerts = cursor.fetchall()

    conn.close()

    return render_template("alerts.html", alerts=alerts)


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("campus_safety.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM alerts")
    alert_count = cursor.fetchone()[0]

    conn.close()

    return render_template("dashboard.html", alert_count=alert_count)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/location")
def location():
    return render_template("location.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)