#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

#define FSR_PIN 34

int16_t ax, ay, az;
int16_t gx, gy, gz;

void setup() {

    Serial.begin(115200);
    delay(1000);

    Serial.println("MPU6050 + FSR Test Starting...");

    Wire.begin(21,22);
    Wire.setClock(100000);

    mpu.initialize();
    mpu.setSleepEnabled(false);

    if (mpu.testConnection()) {
        Serial.println("MPU6050 connected successfully!");
    } else {
        Serial.println("ERROR: MPU6050 connection failed");
    }
}

void loop() {

    // Read MPU6050
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // Read FSR
    int fsrValue = analogRead(FSR_PIN);

    // Print CSV format (best for ML dataset)
    Serial.print(ax); Serial.print(",");
    Serial.print(ay); Serial.print(",");
    Serial.print(az); Serial.print(",");
    Serial.print(gx); Serial.print(",");
    Serial.print(gy); Serial.print(",");
    Serial.print(gz); Serial.print(",");
    Serial.println(fsrValue);

    delay(100);
}