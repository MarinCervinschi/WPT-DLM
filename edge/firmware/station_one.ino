/* DLM Charging Node
    It manages the optical charging simulation. It detects the presence of the vehicle,
    monitors the power/current delivered, and displays the status on an LCD display.
    It communicates with the Raspberry Pi via I2C protocol.

    The circuit:
    * Input: HC-SR04 Ultrasonic Sensor (Trig: Pin 2, Echo: Pin 3)
    * Input: Adafruit INA219 Current/Voltage Sensor (I2C: SDA/SCL)
    * Output: L298N Driver Module (Enable/PWM: Pin 9, Input 1: Pin 8)
    * Output: 12V LED Panel (Connected to Out 1 output of the L298N driver)
    * Output: LCD I2C Display (I2C: SDA/SCL)
*/

#include <Wire.h>
#include <Adafruit_INA219.h>
#include <LiquidCrystal_I2C.h>

// Configuration I2C
const byte SLAVE_ADDRESS = 8;

// Hardware Pins Definition
const int TRIGGER_PIN = 2;
const int ECHO_PIN = 3;
const int PWM_CONTROL_PIN = 9; // Pin ENA of the L298N module
const int DIRECTION_PIN = 8;   // Pin IN1 of the L298N module

// System Constants
const int DETECTION_THRESHOLD_CM = 50;
const unsigned long UPDATE_INTERVAL = 200;

// State Variables
unsigned long lastUpdateTime = 0;
byte isVehiclePresent = 0;
byte isAuthorized = 0;
int currentPowerLevel = 0;
float currentMilliAmps = 0.0;
float busVoltage = 0.0;
float calculatedPower_mW = 0.0;

// Sensor and display initialization
Adafruit_INA219 powerMonitor;
LiquidCrystal_I2C statusDisplay(0x27, 16, 2);

void setup()
{
    // I2C Initialization (Slave)
    Wire.begin(SLAVE_ADDRESS);
    Wire.onRequest(sendTelemetryToMaster);    // Responds to Raspberry Pi
    Wire.onReceive(receiveCommandFromMaster); // Receives power from Raspberry Pi

    // Pin Configuration
    pinMode(TRIGGER_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(PWM_CONTROL_PIN, OUTPUT);
    pinMode(DIRECTION_PIN, OUTPUT);

    // Fixed direction setting for the LED panel
    digitalWrite(DIRECTION_PIN, HIGH);

    // I2C Hardware Initialization
    powerMonitor.begin();
    statusDisplay.init();
    statusDisplay.backlight();

    // Startup Message
    statusDisplay.setCursor(0, 0);
    statusDisplay.print("STATION 1");
    statusDisplay.setCursor(0, 1);
    statusDisplay.print("INITIALIZING...");

    lastUpdateTime = millis();
    Serial.begin(9600);
}

void loop()
{
    if (millis() - lastUpdateTime >= UPDATE_INTERVAL)
    {
        lastUpdateTime = millis();

        // 1. read distance from ultrasonic sensor
        long measuredDistance = readDistance();

        // 2. Update vehicle presence status
        isVehiclePresent = (measuredDistance > 0 && measuredDistance < DETECTION_THRESHOLD_CM) ? 1 : 0;

        // 3. Read electrical telemetry (INA219)
        currentMilliAmps = powerMonitor.getCurrent_mA();
        busVoltage = powerMonitor.getBusVoltage_V();
        calculatedPower_mW = busVoltage * currentMilliAmps;

        // 4. Power actuation (PWM on L298N)
        if (isVehiclePresent == 1 && isAuthorized == 1)
        {
            analogWrite(PWM_CONTROL_PIN, currentPowerLevel);
        }
        else
        {
            analogWrite(PWM_CONTROL_PIN, 0);
            if (isVehiclePresent == 0) { isAuthorized = 0; }
        }

        // 5. Update User Interface (LCD)
        updateStatusDisplay();
    }
}

long readDistance()
{
    digitalWrite(TRIGGER_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIGGER_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIGGER_PIN, LOW);

    long pulseDuration = pulseIn(ECHO_PIN, HIGH);
    int measuredDistance = pulseDuration * 0.034 / 2;

    return measuredDistance;
}

void updateStatusDisplay() {
    statusDisplay.clear();
    statusDisplay.setCursor(0, 0);
    
    if (isVehiclePresent == 1) {
        if (isAuthorized == 1) {
            statusDisplay.print("STATION 1 - CHARGING...");
            statusDisplay.setCursor(0, 1);
            statusDisplay.print("P:"); statusDisplay.print((int)calculatedPower_mW);
            statusDisplay.print("mW L:"); statusDisplay.print(map(currentPowerLevel, 0, 255, 0, 100));
            statusDisplay.print("%");
        } else {
            statusDisplay.print("STATION 1 - VEHICLE DETECTED");
            statusDisplay.setCursor(0, 1);
            statusDisplay.print("SCAN QR CODE...");
        }
    } else {
        statusDisplay.print("STATION 1 - READY");
        statusDisplay.setCursor(0, 1);
        statusDisplay.print("WAITING VEHICLE");
    }
}

void receiveCommandFromMaster(int byteCount) {
    if (Wire.available() >= 2) {
        currentPowerLevel = Wire.read();
        isAuthorized = Wire.read();
    }
}

void sendTelemetryToMaster() {
    byte dataPacket[5];
    dataPacket[0] = isVehiclePresent; 
    
    int currentToSend = (int)currentMilliAmps;
    dataPacket[1] = highByte(currentToSend);
    dataPacket[2] = lowByte(currentToSend);
    
    int voltageToSend = (int)(busVoltage * 10);
    dataPacket[3] = highByte(voltageToSend);
    dataPacket[4] = lowByte(voltageToSend);

    Wire.write(dataPacket, 5);
}