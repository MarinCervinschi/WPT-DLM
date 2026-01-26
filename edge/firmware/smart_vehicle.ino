#include <Arduino.h>

// Hardware Pins Definition
const int PHOTO_SENSOR_PIN = A0;
const int RED_LED_PIN = 11;
const int GREEN_LED_PIN = 10;
const int BLUE_LED_PIN = 9;

// System Constants
const unsigned long UPDATE_INTERVAL = 100; 
const int THRESHOLD_OFF_TO_LOW = 400;  
const int THRESHOLD_LOW_TO_MID = 630;  
const int THRESHOLD_MID_TO_HIGH = 770;

// State Variables
unsigned long lastUpdateTime = 0;
int measuredLight = 0;
int lightPercent = 0; 

void setup() {
    pinMode(RED_LED_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    pinMode(BLUE_LED_PIN, OUTPUT);
    
    Serial.begin(9600);
    lastUpdateTime = millis();
}

void loop() {
    if (millis() - lastUpdateTime >= UPDATE_INTERVAL) {
        lastUpdateTime = millis();

        // 1. Reads how much light arrives from the station panel
        measuredLight = analogRead(PHOTO_SENSOR_PIN);

        // 2. Convert raw value to percentage (0–100)
        lightPercent = map(measuredLight, 0, 1023, 0, 100);

        // 2. Manages visual feedback based on the received POWER
        updatePowerStatusLed();

        // 3. Debug to calibrate thresholds based on ambient light
        Serial.print("Received Light: ");
        Serial.println(measuredLight);
        Serial.print("Light Percentage: ");
        Serial.println(lightPercent);
    }
}

void updatePowerStatusLed() {
    // Usiamo intervalli precisi basati sui raw values
    
    if (measuredLight < THRESHOLD_OFF_TO_LOW) {
        // OFF: Copre il rumore e la luce ambientale (es. 0 - 99)
        setRgbColor(0, 0, 0);
    } 
    else if (measuredLight < THRESHOLD_LOW_TO_MID) {
        // LOW POWER -> Green
        setRgbColor(0, 255, 0);
    }
    else if (measuredLight < THRESHOLD_MID_TO_HIGH) {
        // MEDIUM POWER -> Yellow
        setRgbColor(255, 255, 0);
    }
    else {
        // HIGH POWER -> Red
        setRgbColor(255, 0, 0);
    }
}

void setRgbColor(int red, int green, int blue) {
    analogWrite(RED_LED_PIN, red);
    analogWrite(GREEN_LED_PIN, green);
    analogWrite(BLUE_LED_PIN, blue);
}