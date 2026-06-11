from flask import Flask, request, jsonify, render_template
import smtplib
from email.message import EmailMessage
import threading
import time

app = Flask(__name__)

# ================== EMAIL CONFIG ==================
EMAIL_ADDRESS = "te.guradiansole.k5.6@gmail.com"
EMAIL_PASSWORD = "tkas gbjp rsjx uhqg"
GUARDIAN_EMAIL = "kayasthsamiksha01@gmail.com"

# ================== STATE ==================
current_state = "SAFE"
fall_event_active = False
current_steps = 0

# 🔥 NEW: FALL HOLD SYSTEM
last_fall_time = 0
FALL_DISPLAY_TIME = 5  # seconds

# ================== HOME ==================
@app.route("/")
def home():
    return render_template("index.html")

# ================== STATUS ==================
@app.route("/get-status")
def get_status():
    global current_state, fall_event_active

    # 🔥 HOLD FALL STATE FOR FEW SECONDS
    if fall_event_active:
        if time.time() - last_fall_time > FALL_DISPLAY_TIME:
            fall_event_active = False
            current_state = "SAFE"

    return jsonify({"status": current_state})

# ================== STEPS ==================
@app.route("/send-steps", methods=["POST"])
def receive_steps():
    global current_steps

    data = request.json
    current_steps = data.get("steps", 0)

    print(f"👣 Steps Updated: {current_steps}")

    return jsonify({"status": "ok"})

@app.route("/get-steps")
def get_steps():
    return jsonify({"steps": current_steps})

# ================== EMAIL FUNCTION ==================
def send_email():
    try:
        msg = EmailMessage()
        msg["Subject"] = "🚨 Guardian Sole Emergency Alert"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = GUARDIAN_EMAIL

        msg.set_content("""
Emergency Alert from Guardian Sole

⚠️ FALL DETECTED!
Please check the person immediately.

- Guardian Sole System
""")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print("✅ Email sent")

    except Exception as e:
        print("❌ Email Error:", e)

# ================== ALERT ==================
@app.route("/send-alert", methods=["POST"])
def send_alert():
    global current_state, fall_event_active, last_fall_time

    data = request.json
    status = data.get("status")

    # 🟢 SAFE
    if status == "SAFE":
        current_state = "SAFE"
        fall_event_active = False
        return jsonify({"status": "SAFE"})

    # 🔴 FALL DETECTED
    if status == "FALL DETECTED":

        if not fall_event_active:
            current_state = "FALL DETECTED"
            fall_event_active = True
            last_fall_time = time.time()  # 🔥 IMPORTANT

            # send email in background
            threading.Thread(target=send_email).start()

            return jsonify({"status": "Email sent"})

        return jsonify({"status": "Already alerted"})

    return jsonify({"status": "Invalid request"})

# ================== RUN ==================
if __name__ == "__main__":
    app.run(debug=True)