"""
============================================================================
Mock Arduino Hardware Simulator (Stage 1 Diag + Stage 2 Application Runner)
============================================================================
Thesis Project: Automated Microcontroller Diagnostic & Firmware Management

Simulates an Arduino microcontroller connected over a virtual serial port (e.g. COM11)
Features:
- Robust command parsing (resilient to dirty buffers / reconnects / glued EOF strings)
- Live streaming of Stage 1 hardware self-test diagnostics (RAM, Vcc, GPIO, Analog, I2C, Clock)
- Fault simulation mode via 'CMD:SIM_FAULT' to test UI error boundaries
- Target firmware reception & simulated live application runtime
============================================================================
"""

import serial
import time
import sys

PORT = 'COM11'
BAUD_RATE = 115200

def run_diagnostics(ser, simulate_fault=False):
    print(f"\n[DIAGNOSTICS] Starting hardware diagnostic suite (Fault Injection: {simulate_fault})...")
    
    def send_line(line, delay_s=0.07):
        ser.write((line + '\n').encode('utf-8'))
        ser.flush()
        print(f"  -> {line}")
        time.sleep(delay_s)

    send_line("[DIAG:START]", 0.08)
    
    # 1. RAM Check
    if simulate_fault:
        send_line("[DIAG:RAM:FREE=120;TOTAL=2048;STATUS=WARN;MSG=LOW_MEMORY]")
    else:
        send_line("[DIAG:RAM:FREE=1648;TOTAL=2048;STATUS=OK]")
    
    # 2. Vcc Voltage Check
    if simulate_fault:
        send_line("[DIAG:VCC:VOLTS=3.12;STATUS=FAIL;MSG=UNDERVOLTAGE]")
    else:
        send_line("[DIAG:VCC:VOLTS=5.04;STATUS=OK]")

    # 3. Digital Pins 2..13
    for pin in range(2, 14):
        if simulate_fault and pin == 4:
            send_line(f"[DIAG:GPIO:PIN={pin};STATE=SHORTED_GND;STATUS=FAIL]")
        else:
            send_line(f"[DIAG:GPIO:PIN={pin};STATE=OK;STATUS=OK]")

    # 4. Analog Channels A0..A5
    for a_pin in range(6):
        raw_val = 512 + (a_pin * 45)
        send_line(f"[DIAG:ANALOG:PIN=A{a_pin};RAW={raw_val};STATUS=OK]")

    # 5. I2C Bus Scan
    send_line("[DIAG:I2C:SDA=OK;SCL=OK;DEVICES=1;STATUS=OK]")
    send_line("[DIAG:I2C_DEV:ADDR=0x68;STATUS=FOUND]")  # e.g., MPU6050 / DS3231

    # 6. System Clock Check
    send_line("[DIAG:CLOCK:FREQ=16MHZ;TIMING_US=10012;STATUS=OK]")

    # Final Result
    if simulate_fault:
        send_line("[DIAG:COMPLETE:RESULT=FAIL;CHECKS=21;FAILED=2;ERROR=PIN_4_SHORTED_AND_LOW_VCC]", 0.08)
        print("[DIAGNOSTICS] Diagnostic suite finished with simulated FAULTS.\n")
    else:
        send_line("[DIAG:COMPLETE:RESULT=PASS;CHECKS=21;FAILED=0]", 0.08)
        print("[DIAGNOSTICS] Diagnostic suite PASSED.\n")


def run_target_firmware_loop(ser):
    print("\n[TARGET RUNNER] Target firmware active. Emulating sensor telemetry stream...")
    count = 1
    # Send simulated telemetry readings while checking for interruption
    while count <= 15:
        telemetry = f"[SENSOR_READING] Cycle #{count:03d} | Temp: {22.4 + (count*0.1):.1f}°C | Humidity: {45 + count}% | Pin13: {'HIGH' if count % 2 == 0 else 'LOW'}"
        ser.write((telemetry + '\n').encode('utf-8'))
        ser.flush()
        print(f"  -> {telemetry}")
        
        # Small intervals to remain responsive to incoming commands
        for _ in range(12):
            time.sleep(0.1)
            if ser.in_waiting > 0:
                print("[TARGET RUNNER] New command detected during telemetry. Yielding control.")
                return
        count += 1


def main():
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1.0)
        print("=================================================================")
        print(f"  Mock Arduino running on {PORT} @ {BAUD_RATE} baud")
        print("  Ready for 2-Stage Verification & Flashing requests")
        print("=================================================================\n")

        text_buffer = ""

        # Emit ready banner
        ser.write(b"[SYSTEM:READY] Mock Arduino Initialized (2-Stage Diag Support)\n")
        ser.flush()

        while True:
            if ser.in_waiting > 0:
                try:
                    raw_bytes = ser.read(ser.in_waiting)
                    text_buffer += raw_bytes.decode('utf-8', errors='ignore')

                    while '\n' in text_buffer:
                        line, text_buffer = text_buffer.split('\n', 1)
                        cmd = line.strip()

                        if not cmd:
                            continue

                        print(f"Incoming: {cmd}")

                        # Priority 1: Check for Diagnostic / Control Commands first (even if glued to HEX EOF)
                        if "CMD:DIAG_START" in cmd or cmd == "DIAG":
                            run_diagnostics(ser, simulate_fault=False)

                        elif "CMD:SIM_FAULT" in cmd:
                            run_diagnostics(ser, simulate_fault=True)

                        elif "CMD:PING" in cmd:
                            ser.write(b"[PONG] Mock Arduino Online\n")
                            ser.flush()

                        # Priority 2: Flashing packets / Intel HEX records
                        elif cmd.startswith(":") or "FLASH" in cmd.upper():
                            # If it's the Intel HEX End-Of-File record (:00000001FF)
                            if ":00000001FF" in cmd:
                                print("[FLASH] Intel HEX EOF record reached. Finalizing firmware flash...")
                                ser.write(b"[FLASH:OK] Firmware written to flash memory\n")
                                ser.flush()
                                time.sleep(0.3)
                                run_target_firmware_loop(ser)
                            else:
                                print(f"[FLASH] Chunk received ({len(cmd)} chars)")

                except Exception as e:
                    print(f"Read error: {e}")

            time.sleep(0.01)

    except serial.SerialException as e:
        print(f"\n[ERROR] Could not open {PORT}: {e}")
        print("Please ensure virtual COM port pair is created (e.g. com0com / VSPE COM10 <-> COM11) or check port name.")
    except KeyboardInterrupt:
        print("\nStopping Mock Arduino.")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()