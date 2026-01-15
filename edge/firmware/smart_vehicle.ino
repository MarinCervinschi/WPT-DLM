/* DLM Smart Vehicle - Power Feedback
    It reads the light intensity received from the station and uses the RGB LED 
    to indicate the power range delivered by the DLM system.

    The circuit:
    * Input: Photoresistor (A0) to measure light intensity
    * Output: RGB LED (Red: Pin 6, Yellow/Green: Pin 5, Blue: Pin 3)
*/

#include <Arduino.h>

// Hardware Pins Definition
const int PHOTO_SENSOR_PIN = A0;
const int RED_LED_PIN = 9;
const int GREEN_LED_PIN = 10;
const int BLUE_LED_PIN = 11;

// System Constants
const unsigned long UPDATE_INTERVAL = 100; 
const int NO_LIGHT_THRESHOLD = 0;  
const int LOW_LIGHT_THRESHOLD = 35; 
const int MID_LIGHT_THRESHOLD = 65;

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
        lightPercent = (measuredLight * 100) / 1023;

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
    if (lightPercent == NO_LIGHT_THRESHOLD) {
        // Station Off or Unauthorized: LED Off
        setRgbColor(0, 0, 0);
    } 
    else if (lightPercent <= LOW_LIGHT_THRESHOLD) {
        // LOW POWER: Green (1% - 35%)
        setRgbColor(0, 255, 0);
    }
    else if (lightPercent <= MID_LIGHT_THRESHOLD) {
        // MEDIUM POWER: Yellow (36% - 65%)
        setRgbColor(255, 255, 0);
    }
    else {
        // HIGH POWER: Red (66% - 100%)
        setRgbColor(255, 0, 0);
    }
}

void setRgbColor(int red, int green, int blue) {
    analogWrite(RED_LED_PIN, red);
    analogWrite(GREEN_LED_PIN, green);
    analogWrite(BLUE_LED_PIN, blue);
}