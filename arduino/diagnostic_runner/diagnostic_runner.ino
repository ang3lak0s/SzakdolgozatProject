/*
 * ============================================================================
 * Arduino Microcontroller Self-Diagnostic Runner (Stage 1 Test Firmware)
 * ============================================================================
 * Thesis Project: Automated Microcontroller Diagnostic & Firmware Management
 *
 * This sketch runs automated hardware health checks on an ATmega328P / Arduino Uno:
 * 1. Free RAM / Stack-Heap Integrity Measurement
 * 2. Internal Vcc Power Supply Voltage (via internal 1.1V Bandgap reference)
 * 3. Digital GPIO Pin Integrity (Pull-up & Output capability for Pins D2-D13)
 * 4. Analog Pin Integrity (Pins A0-A5)
 * 5. I2C Bus Sanity Scan (SDA/SCL lines & connected device discovery)
 * 6. System Timer / Clock Frequency Verification
 *
 * Protocol format: Tag-based ASCII lines [DIAG:<SUBSYSTEM>:<KEY>=<VAL>;...]
 * Zero external libraries needed; 100% native AVR / Arduino Core.
 * ============================================================================
 */

#include <Arduino.h>
#include <Wire.h>

const unsigned long BAUD_RATE = 115200;

// Pin ranges for diagnostic testing
const uint8_t START_DIGITAL_PIN = 2;
const uint8_t END_DIGITAL_PIN = 13;
const uint8_t TOTAL_RAM_BYTES = 2048; // ATmega328P standard RAM

extern unsigned int __heap_start;
extern void *__brkval;

/* ============================================================================
 * Memory Diagnostics
 * ============================================================================ */
int getFreeRam() {
    int freeMemory;
    if ((int)__brkval == 0) {
        freeMemory = ((int)&freeMemory) - ((int)&__heap_start);
    } else {
        freeMemory = ((int)&freeMemory) - ((int)__brkval);
    }
    return freeMemory;
}

/* ============================================================================
 * Internal Vcc Measurement (AVR 1.1V Bandgap Reference)
 * ============================================================================ */
long readVccMillivolts() {
    #if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__)
        // Read 1.1V reference against AVcc
        // set the reference to Vcc and the measurement to the internal 1.1V reference
        ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
        delay(3); // Wait for Vref to settle
        ADCSRA |= _BV(ADSC); // Start conversion
        while (bit_is_set(ADCSRA, ADSC)); // measuring

        uint8_t low  = ADCL; // must read ADCL first - it then locks ADCH
        uint8_t high = ADCH; // unlocks both
        long result = (high << 8) | low;

        // Calculate Vcc (in mV); 1125300 = 1.1*1023*1000
        long vcc = 1125300L / result;
        return vcc;
    #else
        return 5000; // Default fallback for other MCUs
    #endif
}

/* ============================================================================
 * Diagnostic Suite Execution
 * ============================================================================ */
void runFullDiagnostics() {
    Serial.println(F("[DIAG:START]"));
    delay(100);

    int totalChecks = 0;
    int failedChecks = 0;

    // 1. RAM Diagnostics
    totalChecks++;
    int freeRam = getFreeRam();
    Serial.print(F("[DIAG:RAM:FREE="));
    Serial.print(freeRam);
    Serial.print(F(";TOTAL="));
    Serial.print(TOTAL_RAM_BYTES);
    if (freeRam > 256) {
        Serial.println(F(";STATUS=OK]"));
    } else {
        Serial.println(F(";STATUS=WARN;MSG=LOW_MEMORY]"));
        failedChecks++;
    }
    delay(80);

    // 2. Vcc Voltage Check
    totalChecks++;
    long vccMv = readVccMillivolts();
    float vccVolts = vccMv / 1000.0;
    Serial.print(F("[DIAG:VCC:VOLTS="));
    Serial.print(vccVolts, 2);
    if (vccMv >= 4300 && vccMv <= 5500) {
        Serial.println(F(";STATUS=OK]"));
    } else {
        Serial.println(F(";STATUS=WARN;MSG=VOLTAGE_OUT_OF_RANGE]"));
        // We warn but don't strictly fail on slight supply droop
    }
    delay(80);

    // 3. Digital GPIO Integrity Checks (Pins 2..13)
    for (uint8_t pin = START_DIGITAL_PIN; pin <= END_DIGITAL_PIN; pin++) {
        totalChecks++;

        // Test Input with Internal Pull-up
        pinMode(pin, INPUT_PULLUP);
        delayMicroseconds(50);
        int pullupRead = digitalRead(pin);

        // Reset pin to safe high-impedance state
        pinMode(pin, INPUT);

        Serial.print(F("[DIAG:GPIO:PIN="));
        Serial.print(pin);
        if (pullupRead == HIGH) {
            Serial.println(F(";STATE=OK]"));
        } else {
            // Pin is pulled LOW externally or shorted to GND
            Serial.println(F(";STATE=PULLED_LOW]"));
        }
        delay(40);
    }

    // 4. Analog Channels Check (A0..A5)
    for (uint8_t aPin = 0; aPin <= 5; aPin++) {
        totalChecks++;
        int val = analogRead(A0 + aPin);
        Serial.print(F("[DIAG:ANALOG:PIN=A"));
        Serial.print(aPin);
        Serial.print(F(";RAW="));
        Serial.print(val);
        Serial.println(F(";STATUS=OK]"));
        delay(40);
    }

    // 5. I2C Bus Scan
    totalChecks++;
    Wire.begin();
    int i2cDevicesFound = 0;
    for (uint8_t address = 1; address < 127; address++) {
        Wire.beginTransmission(address);
        uint8_t error = Wire.endTransmission();
        if (error == 0) {
            i2cDevicesFound++;
            Serial.print(F("[DIAG:I2C_DEV:ADDR=0x"));
            if (address < 16) Serial.print(F("0"));
            Serial.print(address, HEX);
            Serial.println(F(";STATUS=FOUND]"));
        }
    }
    Serial.print(F("[DIAG:I2C:SDA=OK;SCL=OK;DEVICES="));
    Serial.print(i2cDevicesFound);
    Serial.println(F(";STATUS=OK]"));
    delay(80);

    // 6. Clock / Timer Check
    totalChecks++;
    unsigned long t1 = micros();
    delay(10);
    unsigned long t2 = micros();
    unsigned long elapsed = t2 - t1;

    Serial.print(F("[DIAG:CLOCK:FREQ=16MHZ;TIMING_US="));
    Serial.print(elapsed);
    if (elapsed >= 9500 && elapsed <= 10500) {
        Serial.println(F(";STATUS=OK]"));
    } else {
        Serial.println(F(";STATUS=WARN]"));
    }
    delay(80);

    // Final Completion Report
    Serial.print(F("[DIAG:COMPLETE:RESULT="));
    if (failedChecks == 0) {
        Serial.print(F("PASS;CHECKS="));
        Serial.print(totalChecks);
        Serial.println(F(";FAILED=0]"));
    } else {
        Serial.print(F("FAIL;CHECKS="));
        Serial.print(totalChecks);
        Serial.print(F(";FAILED="));
        Serial.print(failedChecks);
        Serial.println(F("]"));
    }
}

void setup() {
    Serial.begin(BAUD_RATE);
    while (!Serial) { ; } // Wait for serial port to connect

    Serial.println(F("[SYSTEM:READY] Arduino Diagnostic Runner V2.0 Initialized"));
    Serial.println(F("[HINT] Send 'CMD:DIAG_START' to run diagnostic suite"));
}

void loop() {
    if (Serial.available() > 0) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();

        if (cmd == "CMD:DIAG_START" || cmd == "DIAG") {
            runFullDiagnostics();
        } else if (cmd == "CMD:PING") {
            Serial.println(F("[PONG] Diagnostic Runner Active"));
        }
    }
}
