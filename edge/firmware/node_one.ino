#include <Adafruit_INA219.h>

// Hardware Pins Definition
const int TRIGGER_PIN = 2;
const int ECHO_PIN = 3;
const int PWM_CONTROL_PIN = 9; 
const int DIRECTION_PIN = 8;   

// System Constants
const int DETECTION_THRESHOLD_CM = 50;
const unsigned long DISPLAY_UPDATE_INTERVAL = 500;

// State Variables
unsigned long lastDisplayTime = 0;
byte isVehiclePresent = 0;
String status = "OFF";
int pwmLevel = 0;

// Variabili per telemetria
long distance = 0;
float current = 0.0;
float voltage = 0.0;
float power = 0.0;

// Sensor and display initialization
Adafruit_INA219 powerMonitor;

void setup()
{
    Serial.begin(115200);

    // Pin Configuration
    pinMode(TRIGGER_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(PWM_CONTROL_PIN, OUTPUT);
    pinMode(DIRECTION_PIN, OUTPUT);

    // Fixed direction setting
    digitalWrite(DIRECTION_PIN, HIGH);

    // Hardware Initialization
    if (!powerMonitor.begin()) {
        // Se INA219 fallisce, segnalalo su seriale
        Serial.println("ERROR: INA219 NOT FOUND");
    }
}

void loop()
{
    distance = readDistance();
    isVehiclePresent = (distance > 0 && distance <= DETECTION_THRESHOLD_CM) ? 1 : 0;

    voltage = powerMonitor.getBusVoltage_V();
    current = powerMonitor.getCurrent_mA();
    power = voltage * (current / 1000.0);

    // 1. SERIAL COMUNICATION (Priority)
    if (Serial.available() > 0) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        handleSerialCommunication(cmd);
    }

    // 2. SENSOR READINGS & ACTUATION
    if (isVehiclePresent == 1 && status == "ON")
    {
        analogWrite(PWM_CONTROL_PIN, pwmLevel);
    }
    else
    {
        analogWrite(PWM_CONTROL_PIN, 0);
        // If the vehicle leaves, set status to OFF
        if (isVehiclePresent == 0) { 
            status = "OFF"; 
            pwmLevel = 0;
        }
    }

    // 3. UPDATE INTERFACE (LCD)
    if (millis() - lastDisplayTime >= DISPLAY_UPDATE_INTERVAL) {
        lastDisplayTime = millis();
    }
}

void handleSerialCommunication(String cmd) {

    if (cmd == "GET:DIST") {
        distance = readDistance();        
        // Rispondiamo con un tag per sicurezza
        Serial.print("DIST:");
        Serial.println(distance);
    } 
    else if (cmd == "GET:PWR") {
        voltage = powerMonitor.getBusVoltage_V();
        current = powerMonitor.getCurrent_mA();
        power = voltage * (current / 1000.0); 
       
        Serial.print("PWR:");
        Serial.print(voltage);
        Serial.print(":");
        Serial.print(current / 1000.0);
        Serial.print(":");
        Serial.println(power);
    }    
    else if (cmd.startsWith("SET:L298:")) {
        int firstColon = cmd.indexOf(':', 8);             
        int secondColon = cmd.lastIndexOf(':'); 
    
        if (firstColon > 0 && secondColon > 0) {
            String pwmString = cmd.substring(firstColon + 1, secondColon);
            String statusString = cmd.substring(secondColon + 1);

            pwmLevel = pwmString.toInt(); 
            
            if (statusString == "ON") {
                status = "ON";
            } else {
                status = "OFF";
            } 
        }
    }
}

long readDistance()
{
    digitalWrite(TRIGGER_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIGGER_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIGGER_PIN, LOW);

    long pulseDuration = pulseIn(ECHO_PIN, HIGH, 30000); 
    
    if (pulseDuration == 0) return 999;

    int measuredDistance = pulseDuration * 0.034 / 2;
    return measuredDistance;
}