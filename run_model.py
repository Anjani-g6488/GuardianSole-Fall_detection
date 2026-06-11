import serial
import numpy as np
import tensorflow as tf
import time
import requests

# ================== LOAD MODEL ==================
model = tf.keras.models.load_model("fall_detection_cnn_lstm.h5")

# ================== SERIAL ==================
ser = serial.Serial('COM3', 115200, timeout=1)

print("🔥 Guardian Sole System (Corrected Mode)")

# ================== SETTINGS ==================
ACC_THRESHOLD = 2.5   # 
FSR_THRESHOLD = 250

# ================== STEP SETTINGS ==================
STEP_THRESHOLD = 1.15
STEP_DELAY = 0.35
ALPHA = 0.8

# ================== STATE ==================
last_sent_status = "SAFE"

# 👣 Step variables
step_count = 0
last_step_time = 0
prev_acc_mag = 0
filtered_acc = 0
last_sent_steps = 0

# ================== LOOP ==================
while True:
    try:
        line = ser.readline().decode(errors='ignore').strip()

        if line.count(",") != 6:
            continue

        ax, ay, az, gx, gy, gz, fsr = map(float, line.split(","))

        # 🔹 Normalize
        ax /= 16384.0
        ay /= 16384.0
        az /= 16384.0

        gx /= 131.0
        gy /= 131.0
        gz /= 131.0

        # 🔹 Acc magnitude
        acc_mag = (ax**2 + ay**2 + az**2) ** 0.5

        print(f"\n📡 FSR:{fsr:.0f} | Acc:{acc_mag:.2f}")

        # ================== STEP DETECTION ==================
        filtered_acc = ALPHA * filtered_acc + (1 - ALPHA) * acc_mag
        current_time = time.time()

        if filtered_acc > STEP_THRESHOLD and prev_acc_mag <= STEP_THRESHOLD:

            if current_time - last_step_time > STEP_DELAY:
                step_count += 1
                last_step_time = current_time

                print(f"👣 Steps: {step_count}")

                # send only when step increases
                if step_count > last_sent_steps:
                    try:
                        requests.post(
                            "http://127.0.0.1:5000/send-steps",
                            json={"steps": step_count},
                            timeout=1
                        )
                        last_sent_steps = step_count
                    except:
                        pass

        prev_acc_mag = filtered_acc

        # ================== FALL DETECTION (FIXED) ==================
        if acc_mag > ACC_THRESHOLD and fsr < FSR_THRESHOLD:

            print("🚨 FALL DETECTED 🚨")

            if last_sent_status != "FALL":
                try:
                    requests.post(
                        "http://127.0.0.1:5000/send-alert",
                        json={"status": "FALL DETECTED"},
                        timeout=1
                    )
                    print("📡 FALL SENT TO SERVER")
                except:
                    print("⚠️ Server not reachable")

                last_sent_status = "FALL"

        # ================== WALK ==================
        elif acc_mag > 1.05:
            print("🚶 WALKING")
            last_sent_status = "WALKING"

        # ================== SAFE ==================
        else:
            print("✅ SAFE")
            last_sent_status = "SAFE"

    except Exception as e:
        print("❌ Error:", e)