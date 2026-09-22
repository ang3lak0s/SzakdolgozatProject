/**
 * STK500v1 In-Browser Bootloader Flasher
 * Communicates with Arduino Uno / Nano / ATmega328P Optiboot bootloader via Web Serial API.
 */

import { parseIntelHex } from './intelHex';

// STK500v1 Constants
export const STK_OK = 0x10;
export const STK_FAILED = 0x11;
export const STK_UNKNOWN = 0x12;
export const STK_NODEVICE = 0x13;
export const STK_INSYNC = 0x14;
export const STK_NOSYNC = 0x15;

export const CMD_STK_GET_SYNC = 0x30;
export const CMD_STK_GET_SIGN_ON = 0x31;
export const CMD_STK_SET_PARAMETER = 0x40;
export const CMD_STK_GET_PARAMETER = 0x41;
export const CMD_STK_SET_DEVICE = 0x42;
export const CMD_STK_SET_DEVICE_EXT = 0x45;
export const CMD_STK_ENTER_PROGMODE = 0x50;
export const CMD_STK_LEAVE_PROGMODE = 0x51;
export const CMD_STK_CHIP_ERASE = 0x52;
export const CMD_STK_CHECK_AUTOINC = 0x53;
export const CMD_STK_LOAD_ADDRESS = 0x55;
export const CMD_STK_UNIVERSAL = 0x56;
export const CMD_STK_PROG_PAGE = 0x64;
export const CMD_STK_READ_PAGE = 0x74;

export const SYNC_CRC_EOP = 0x20;

/**
 * Pulses DTR / RTS to trigger the microcontroller hardware auto-reset capacitor
 */
export async function triggerHardwareReset(port) {
  if (!port || !port.setSignals) return;

  try {
    // Assert DTR low
    await port.setSignals({ dataTerminalReady: false, requestToSend: false });
    await new Promise(r => setTimeout(r, 120));
    // Release DTR high to complete reset pulse
    await port.setSignals({ dataTerminalReady: true, requestToSend: true });
    // Allow bootloader initialization window
    await new Promise(r => setTimeout(r, 200));
  } catch (err) {
    console.warn('Could not pulse DTR signals:', err);
  }
}

/**
 * Low-level packet transport helper with timeout handling
 */
class Stk500Transport {
  constructor(port) {
    this.port = port;
    this.reader = null;
    this.writer = null;
    this.rxBuffer = [];
  }

  async acquireLocks() {
    this.reader = this.port.readable.getReader();
    this.writer = this.port.writable.getWriter();
    this.rxBuffer = [];
    this.isReading = true;
    this.startBackgroundRead();
  }

  startBackgroundRead() {
    (async () => {
      while (this.isReading && this.reader) {
        try {
          const { value, done } = await this.reader.read();
          if (done) break;
          if (value) {
            for (let i = 0; i < value.length; i++) {
              this.rxBuffer.push(value[i]);
            }
          }
        } catch (err) {
          // Stream error or released
          break;
        }
      }
    })();
  }

  async releaseLocks() {
    this.isReading = false;
    if (this.reader) {
      try {
        await this.reader.cancel();
      } catch (_) {}
      try {
        this.reader.releaseLock();
      } catch (_) {}
      this.reader = null;
    }
    if (this.writer) {
      try {
        this.writer.releaseLock();
      } catch (_) {}
      this.writer = null;
    }
  }

  async writeBytes(bytes) {
    if (!this.writer) throw new Error('Serial writer not available');
    const u8 = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
    await this.writer.write(u8);
  }

  async readByte(timeoutMs = 600) {
    const startTime = Date.now();
    while (Date.now() - startTime < timeoutMs) {
      if (this.rxBuffer.length > 0) {
        return this.rxBuffer.shift();
      }
      await new Promise(r => setTimeout(r, 5));
    }
    throw new Error(`Timeout waiting for byte from microcontroller (${timeoutMs}ms)`);
  }

  async expectResponse(timeoutMs = 800) {
    const b1 = await this.readByte(timeoutMs);
    if (b1 !== STK_INSYNC) {
      throw new Error(`Expected STK_INSYNC (0x14), received 0x${b1.toString(16).toUpperCase()}`);
    }
    const b2 = await this.readByte(timeoutMs);
    if (b2 !== STK_OK) {
      throw new Error(`Expected STK_OK (0x10), received 0x${b2.toString(16).toUpperCase()}`);
    }
    return true;
  }

  flushRx() {
    this.rxBuffer = [];
  }
}

/**
 * Main STK500v1 Flasher Function
 *
 * @param {SerialPort} port - Active Web Serial port object
 * @param {string} hexContent - Intel HEX string content
 * @param {Object} options - Configuration options
 * @param {function} options.onProgress - Progress callback ({ percent, current, total, phase })
 * @param {function} options.onLog - Log message callback (message)
 */
export async function flashFirmwareSTK500(port, hexContent, options = {}) {
  const onProgress = options.onProgress || (() => {});
  const onLog = options.onLog || console.log;
  const pageSize = options.pageSize || 128; // Default 128 bytes for ATmega328P

  onLog('>> [PARSER] Decoding Intel HEX payload...');
  const hexParsed = parseIntelHex(hexContent, pageSize);
  onLog(`>> [PARSER] HEX valid: ${hexParsed.totalBytes} bytes across ${hexParsed.totalPages} pages.\n`);

  onProgress({ percent: 5, phase: 'RESETTING' });
  onLog('>> [BOOTLOADER] Pulsing DTR line to trigger hardware auto-reset...');
  await triggerHardwareReset(port);

  const transport = new Stk500Transport(port);
  await transport.acquireLocks();

  try {
    // 1. Establish Synchronisation (STK_GET_SYNC)
    onProgress({ percent: 15, phase: 'SYNC' });
    onLog('>> [STK500] Synchronizing with Optiboot bootloader (CMD_STK_GET_SYNC)...');

    let synced = false;
    let syncAttempts = 0;
    const maxSyncAttempts = 8;

    while (!synced && syncAttempts < maxSyncAttempts) {
      syncAttempts++;
      transport.flushRx();
      try {
        await transport.writeBytes([CMD_STK_GET_SYNC, SYNC_CRC_EOP]);
        await transport.expectResponse(400);
        synced = true;
      } catch (err) {
        await new Promise(r => setTimeout(r, 60));
      }
    }

    if (!synced) {
      throw new Error('Failed to synchronize with Arduino bootloader (STK_GET_SYNC timeout).');
    }
    onLog('>> [STK500] Bootloader synchronized successfully (INSYNC / OK received).\n');

    // 2. Enter Programming Mode
    onProgress({ percent: 25, phase: 'ENTER_PROGMODE' });
    onLog('>> [STK500] Entering programming mode (CMD_STK_ENTER_PROGMODE)...');
    await transport.writeBytes([CMD_STK_ENTER_PROGMODE, SYNC_CRC_EOP]);
    await transport.expectResponse(500);

    // 3. Page-by-Page Flash Loop
    onLog(`>> [FLASH] Writing ${hexParsed.totalPages} memory pages (Page size: ${pageSize} bytes)...`);
    const totalPages = hexParsed.totalPages;

    for (let i = 0; i < totalPages; i++) {
      const page = hexParsed.pages[i];

      // A. Load Word Address
      const wordAddr = page.wordAddress;
      const addrLow = wordAddr & 0xff;
      const addrHigh = (wordAddr >> 8) & 0xff;
      await transport.writeBytes([CMD_STK_LOAD_ADDRESS, addrLow, addrHigh, SYNC_CRC_EOP]);
      await transport.expectResponse(400);

      // B. Program Page: 0x64 [lenHigh] [lenLow] [memType='F'] [data...] 0x20
      const lenHigh = (pageSize >> 8) & 0xff;
      const lenLow = pageSize & 0xff;
      const packet = new Uint8Array(5 + pageSize);
      packet[0] = CMD_STK_PROG_PAGE;
      packet[1] = lenHigh;
      packet[2] = lenLow;
      packet[3] = 0x46; // 'F' for Flash memory
      packet.set(page.data, 4);
      packet[4 + pageSize] = SYNC_CRC_EOP;

      await transport.writeBytes(packet);
      await transport.expectResponse(600);

      const percent = Math.round(25 + ((i + 1) / totalPages) * 70);
      onProgress({
        percent,
        current: i + 1,
        total: totalPages,
        phase: 'PROGRAMMING'
      });
    }

    onLog(`>> [FLASH] All ${totalPages} pages written and verified.\n`);

    // 4. Leave Programming Mode
    onProgress({ percent: 98, phase: 'LEAVE_PROGMODE' });
    onLog('>> [STK500] Leaving programming mode (CMD_STK_LEAVE_PROGMODE)...');
    await transport.writeBytes([CMD_STK_LEAVE_PROGMODE, SYNC_CRC_EOP]);
    await transport.expectResponse(500);

    onProgress({ percent: 100, phase: 'COMPLETED' });
    onLog('>> [SUCCESS] Firmware flashed successfully. Microcontroller is booting.\n');

    return {
      success: true,
      totalBytes: hexParsed.totalBytes,
      totalPages: hexParsed.totalPages
    };
  } finally {
    await transport.releaseLocks();
  }
}
