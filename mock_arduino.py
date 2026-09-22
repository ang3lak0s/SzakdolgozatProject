"""
============================================================================
Mock Arduino Hardware Simulator (Stage 1 Diag + STK500v1 Bootloader Runner)
============================================================================
Thesis Project: Automated Microcontroller Diagnostic & Firmware Management

Simulates an Arduino microcontroller connected over a virtual serial port (e.g. COM11)
Features:
- Live streaming of Stage 1 hardware self-test diagnostics (RAM, Vcc, GPIO, Analog, I2C, Clock)
- Fault simulation mode via 'CMD:SIM_FAULT' to test UI error boundaries
- Full STK500v1 Optiboot bootloader protocol emulation (GET_SYNC, PROGMODE, LOAD_ADDR, PROG_PAGE, LEAVE_PROGMODE)
- Target firmware execution and live telemetry streaming after flashing
============================================================================
"""

import serial
import time
import sys

PORT = 'COM11'
BAUD_RATE = 115200

# STK500 Constants
STK_OK = 0x10
STK_INSYNC = 0x14
CMD_STK_GET_SYNC = 0x30
CMD_STK_ENTER_PROGMODE = 0x50
CMD_STK_LEAVE_PROGMODE = 0x51
CMD_STK_LOAD_ADDRESS = 0x55
CMD_STK_PROG_PAGE = 0x64
SYNC_CRC_EOP = 0x20

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
    send_line("[DIAG:I2C_DEV:ADDR=0x68;STATUS=FOUND]")

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
    while count <= 20:
        telemetry = f"[SENSOR_READING] Cycle #{count:03d} | Temp: {22.4 + (count*0.1):.1f}C | Humidity: {45 + count}% | Pin13: {'HIGH' if count % 2 == 0 else 'LOW'}"
        ser.write((telemetry + '\n').encode('utf-8'))
        ser.flush()
        print(f"  -> {telemetry}")
        
        for _ in range(12):
            time.sleep(0.1)
            if ser.in_waiting > 0:
                print("[TARGET RUNNER] New incoming serial data detected. Yielding runner.")
                return
        count += 1


def main():
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=0.1)
        print("=================================================================")
        print(f"  Mock Arduino running on {PORT} @ {BAUD_RATE} baud")
        print("  Ready for Stage 1 Diagnostics and STK500v1 Bootloader Flashing")
        print("=================================================================\n")

        # Emit ready banner
        ser.write(b"[SYSTEM:READY] Mock Arduino Initialized (Diagnostic + STK500 Support)\n")
        ser.flush()

        rx_byte_buffer = bytearray()
        pages_written = 0

        while True:
            if ser.in_waiting > 0:
                new_data = ser.read(ser.in_waiting)
                rx_byte_buffer.extend(new_data)

                # Process buffer
                while len(rx_byte_buffer) > 0:
                    first_byte = rx_byte_buffer[0]

                    # -------------------------------------------------------------
                    # STK500 Binary Command Handling
                    # -------------------------------------------------------------
                    if first_byte == CMD_STK_GET_SYNC:
                        # Expect: 0x30 0x20
                        if len(rx_byte_buffer) < 2:
                            break
                        if rx_byte_buffer[1] == SYNC_CRC_EOP:
                            ser.write(bytes([STK_INSYNC, STK_OK]))
                            ser.flush()
                            print("[STK500] Sync handshake (CMD_STK_GET_SYNC) -> INSYNC / OK sent")
                            rx_byte_buffer = rx_byte_buffer[2:]
                            pages_written = 0
                            continue
                        else:
                            rx_byte_buffer.pop(0)
                            continue

                    elif first_byte == CMD_STK_ENTER_PROGMODE:
                        # Expect: 0x50 0x20
                        if len(rx_byte_buffer) < 2:
                            break
                        if rx_byte_buffer[1] == SYNC_CRC_EOP:
                            ser.write(bytes([STK_INSYNC, STK_OK]))
                            ser.flush()
                            print("[STK500] Entered programming mode (CMD_STK_ENTER_PROGMODE)")
                            rx_byte_buffer = rx_byte_buffer[2:]
                            continue
                        else:
                            rx_byte_buffer.pop(0)
                            continue

                    elif first_byte == CMD_STK_LOAD_ADDRESS:
                        # Expect: 0x55 <addrLow> <addrHigh> 0x20 (4 bytes)
                        if len(rx_byte_buffer) < 4:
                            break
                        if rx_byte_buffer[3] == SYNC_CRC_EOP:
                            addr_word = rx_byte_buffer[1] | (rx_byte_buffer[2] << 8)
                            ser.write(bytes([STK_INSYNC, STK_OK]))
                            ser.flush()
                            rx_byte_buffer = rx_byte_buffer[4:]
                            continue
                        else:
                            rx_byte_buffer.pop(0)
                            continue

                    elif first_byte == CMD_STK_PROG_PAGE:
                        # Expect: 0x64 <lenH> <lenL> <memType='F'> <data bytes...> 0x20
                        if len(rx_byte_buffer) < 5:
                            break
                        page_len = (rx_byte_buffer[1] << 8) | rx_byte_buffer[2]
                        total_expected = 4 + page_len + 1  # 4 header bytes + data + 1 EOP byte
                        if len(rx_byte_buffer) < total_expected:
                            break # Wait for remaining page bytes
                        
                        if rx_byte_buffer[total_expected - 1] == SYNC_CRC_EOP:
                            pages_written += 1
                            ser.write(bytes([STK_INSYNC, STK_OK]))
                            ser.flush()
                            print(f"[STK500] Programmed Page #{pages_written:02d} ({page_len} bytes)")
                            rx_byte_buffer = rx_byte_buffer[total_expected:]
                            continue
                        else:
                            rx_byte_buffer.pop(0)
                            continue

                    elif first_byte == CMD_STK_LEAVE_PROGMODE:
                        # Expect: 0x51 0x20
                        if len(rx_byte_buffer) < 2:
                            break
                        if rx_byte_buffer[1] == SYNC_CRC_EOP:
                            ser.write(bytes([STK_INSYNC, STK_OK]))
                            ser.flush()
                            print(f"[STK500] Programming completed ({pages_written} pages total). Booting target application...")
                            rx_byte_buffer = rx_byte_buffer[2:]
                            time.sleep(0.3)
                            ser.write(b"[FLASH:OK] Firmware flashed via STK500 protocol\n")
                            ser.flush()
                            run_target_firmware_loop(ser)
                            continue
                        else:
                            rx_byte_buffer.pop(0)
                            continue

                    # -------------------------------------------------------------
                    # ASCII Text Command Handling (Stage 1 Diagnostics & Utils)
                    # -------------------------------------------------------------
                    if b'\n' in rx_byte_buffer:
                        line_bytes, rx_byte_buffer = rx_byte_buffer.split(b'\n', 1)
                        line = line_bytes.decode('utf-8', errors='ignore').strip()
                        if not line:
                            continue

                        print(f"Incoming: {line}")
                        if "CMD:DIAG_START" in line or line == "DIAG":
                            run_diagnostics(ser, simulate_fault=False)
                        elif "CMD:SIM_FAULT" in line:
                            run_diagnostics(ser, simulate_fault=True)
                        elif "CMD:PING" in line:
                            ser.write(b"[PONG] Mock Arduino Online\n")
                            ser.flush()
                        continue

                    # If first byte is non-STK and no newline yet, wait for more data
                    break

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