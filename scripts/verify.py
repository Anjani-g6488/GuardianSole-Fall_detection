import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dense, Input

# ----------------------------
# CONFIG
# ----------------------------

DATA_PATH = "dataset/SisFall"
WINDOW_SIZE = 400
STEP_SIZE = 200

print("Checking dataset folder...")

if not os.path.exists(DATA_PATH):
    print("ERROR: Dataset folder not found:", DATA_PATH)
    exit()

print("Dataset folders:", os.listdir(DATA_PATH))


# ----------------------------
# LOAD DATA
# ----------------------------

def load_data():

    data = []
    labels = []

    for root, dirs, files in os.walk(DATA_PATH):

        for file in files:

            if not file.endswith(".txt"):
                continue

            filepath = os.path.join(root, file)

            rows = []

            with open(filepath, "r", encoding="latin1") as f:

                for line in f:

                    line = line.strip()

                    if not line:
                        continue

                    line = line.replace(";", "")
                    parts = line.split(",")

                    if len(parts) >= 6:

                        try:
                            values = [float(x) for x in parts[:6]]
                            rows.append(values)
                        except:
                            continue

            if len(rows) == 0:
                continue

            # D01–D19 → fall
            # D20–D38 → ADL

            activity = int(file.split("_")[0][1:])
            label = 1 if activity <= 19 else 0

            data.append(np.array(rows))
            labels.append(label)

    return data, labels


# ----------------------------
# CREATE SLIDING WINDOWS
# ----------------------------

def create_windows(data, labels):

    X = []
    y = []

    for signal, label in zip(data, labels):

        if len(signal) < WINDOW_SIZE:
            continue

        for i in range(0, len(signal) - WINDOW_SIZE + 1, STEP_SIZE):

            window = signal[i:i + WINDOW_SIZE]

            X.append(window)
            y.append(label)

    return np.array(X), np.array(y)


# ----------------------------
# FEATURE EXTRACTION
# ----------------------------

def extract_features(X):

    features = []

    for window in X:

        mean = np.mean(window, axis=0)
        std = np.std(window, axis=0)
        max_ = np.max(window, axis=0)
        min_ = np.min(window, axis=0)

        feat = np.concatenate([mean, std, max_, min_])

        features.append(feat)

    return np.array(features)


# ----------------------------
# MAIN
# ----------------------------

if __name__ == "__main__":

    print("\nLoading SisFall dataset...")

    data, labels = load_data()

    print("Files Loaded:", len(data))

    if len(data) == 0:
        print("ERROR: Dataset not detected.")
        exit()

    print("\nCreating sliding windows...")

    X, y = create_windows(data, labels)

    print("Total windows:", X.shape)

    if len(X) == 0:
        print("ERROR: No windows created.")
        exit()

    # Dataset statistics
    print("\nFall samples:", np.sum(y))
    print("Non-fall samples:", len(y) - np.sum(y))

    # ----------------------------
    # NORMALIZATION
    # ----------------------------

    scaler = StandardScaler()

    X_reshaped = X.reshape(-1, 6)
    X_scaled = scaler.fit_transform(X_reshaped)

    X = X_scaled.reshape(-1, WINDOW_SIZE, 6)

    # ----------------------------
    # TRAIN TEST SPLIT
    # ----------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # ==========================================================
    # MODEL 1 — RANDOM FOREST
    # ==========================================================

    print("\nTraining Random Forest...")

    X_train_feat = extract_features(X_train)
    X_test_feat = extract_features(X_test)

    rf_model = RandomForestClassifier(n_estimators=100)

    rf_model.fit(X_train_feat, y_train)

    y_pred_rf = rf_model.predict(X_test_feat)

    print("\nRandom Forest Results")
    print(classification_report(y_test, y_pred_rf))
    print("Confusion Matrix\n", confusion_matrix(y_test, y_pred_rf))

    # ==========================================================
    # MODEL 2 — CNN + LSTM
    # ==========================================================

    print("\nTraining CNN + LSTM...")

    model = Sequential([
        Input(shape=(WINDOW_SIZE, 6)),
        Conv1D(64, 3, activation='relu'),
        MaxPooling1D(2),
        Conv1D(128, 3, activation='relu'),
        MaxPooling1D(2),
        LSTM(64),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    model.fit(
        X_train,
        y_train,
        epochs=10,
        batch_size=32,
        validation_split=0.2
    )
    model.save("fall_detection_cnn_lstm.h5")

    loss, accuracy = model.evaluate(X_test, y_test)

    print("\nCNN Test Accuracy:", accuracy)