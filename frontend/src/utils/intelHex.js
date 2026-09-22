/**
 * Intel HEX Parser Utility
 * Parses standard Intel HEX 8-bit / 16-bit ASCII records into page-aligned binary buffers.
 */

export function parseIntelHex(hexString, pageSize = 128) {
  if (!hexString || typeof hexString !== 'string') {
    throw new Error('Invalid or empty HEX string provided.');
  }

  const lines = hexString.split(/\r?\n/);
  const memoryMap = new Map(); // address -> byte
  let extendedAddress = 0;
  let minAddress = Infinity;
  let maxAddress = 0;

  for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
    const rawLine = lines[lineIndex].trim();
    if (!rawLine) continue;

    if (!rawLine.startsWith(':')) {
      // Ignore non-record lines or comments
      continue;
    }

    if (rawLine.length < 11) {
      throw new Error(`Corrupted Intel HEX line ${lineIndex + 1}: line too short.`);
    }

    // Parse record fields
    const byteCount = parseInt(rawLine.substr(1, 2), 16);
    const address = parseInt(rawLine.substr(3, 4), 16);
    const recordType = parseInt(rawLine.substr(7, 2), 16);
    const dataHex = rawLine.substr(9, byteCount * 2);
    const checksum = parseInt(rawLine.substr(9 + byteCount * 2, 2), 16);

    // Verify Checksum: sum of all bytes in line including length, address, type, data, checksum == 0 (mod 256)
    let sum = byteCount + ((address >> 8) & 0xff) + (address & 0xff) + recordType + checksum;
    for (let i = 0; i < byteCount; i++) {
      sum += parseInt(dataHex.substr(i * 2, 2), 16);
    }

    if ((sum & 0xff) !== 0) {
      throw new Error(`Checksum mismatch on Intel HEX line ${lineIndex + 1}.`);
    }

    if (recordType === 0x00) {
      // Data Record
      const baseAddr = extendedAddress + address;
      for (let i = 0; i < byteCount; i++) {
        const byteVal = parseInt(dataHex.substr(i * 2, 2), 16);
        const targetAddr = baseAddr + i;
        memoryMap.set(targetAddr, byteVal);
        if (targetAddr < minAddress) minAddress = targetAddr;
        if (targetAddr > maxAddress) maxAddress = targetAddr;
      }
    } else if (recordType === 0x01) {
      // End Of File Record
      break;
    } else if (recordType === 0x02) {
      // Extended Segment Address Record
      extendedAddress = parseInt(dataHex, 16) << 4;
    } else if (recordType === 0x04) {
      // Extended Linear Address Record
      extendedAddress = parseInt(dataHex, 16) << 16;
    }
  }

  if (memoryMap.size === 0) {
    throw new Error('No valid data records found in HEX file.');
  }

  const startAddress = minAddress === Infinity ? 0 : minAddress;
  const endAddress = maxAddress;
  const totalBytes = endAddress - startAddress + 1;

  // Flatten into contiguous Uint8Array padded with 0xFF (standard unprogrammed flash state)
  const binaryData = new Uint8Array(totalBytes);
  binaryData.fill(0xff);

  for (let addr = startAddress; addr <= endAddress; addr++) {
    if (memoryMap.has(addr)) {
      binaryData[addr - startAddress] = memoryMap.get(addr);
    }
  }

  // Segment into page-aligned blocks for STK500 page programming
  const totalPages = Math.ceil(totalBytes / pageSize);
  const pages = [];

  for (let p = 0; p < totalPages; p++) {
    const pageStartByteAddr = startAddress + p * pageSize;
    const pageBuffer = new Uint8Array(pageSize);
    pageBuffer.fill(0xff);

    for (let b = 0; b < pageSize; b++) {
      const currentAddr = pageStartByteAddr + b;
      if (memoryMap.has(currentAddr)) {
        pageBuffer[b] = memoryMap.get(currentAddr);
      }
    }

    pages.push({
      pageIndex: p,
      byteAddress: pageStartByteAddr,
      wordAddress: pageStartByteAddr >> 1, // AVR flash is 16-bit word addressed
      data: pageBuffer
    });
  }

  return {
    startAddress,
    endAddress,
    totalBytes,
    pageSize,
    totalPages,
    pages,
    binaryData
  };
}
