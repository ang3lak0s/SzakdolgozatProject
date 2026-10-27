import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools" / "ArduinoCore-avr"
CORE = TOOLS / "cores" / "arduino"
VARIANT = TOOLS / "variants" / "standard"
WIRE = TOOLS / "libraries" / "Wire" / "src"

BUILD_DIR = ROOT / "arduino" / "build"
BUILD_DIR.mkdir(parents=True, exist_ok=True)

AVR_BIN = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links"
if not (AVR_BIN / "avr-gcc.exe").exists():
    # Try finding in PATH
    import shutil
    gcc_path = shutil.which("avr-gcc")
    if gcc_path:
        AVR_BIN = Path(gcc_path).parent

print(f"Using AVR toolchain at: {AVR_BIN}")

CC = str(AVR_BIN / "avr-gcc.exe")
CXX = str(AVR_BIN / "avr-g++.exe")
AR = str(AVR_BIN / "avr-ar.exe")
OBJCOPY = str(AVR_BIN / "avr-objcopy.exe")
SIZE = str(AVR_BIN / "avr-size.exe")

CFLAGS = [
    "-c", "-g", "-Os", "-w", "-ffunction-sections", "-fdata-sections",
    "-MMD", "-mmcu=atmega328p", "-DF_CPU=16000000L", "-DARDUINO=10819",
    "-DARDUINO_AVR_UNO", "-DARDUINO_ARCH_AVR",
    f"-I{CORE}", f"-I{VARIANT}", f"-I{WIRE}", f"-I{WIRE / 'utility'}"
]

CXXFLAGS = CFLAGS + ["-fno-exceptions", "-fno-threadsafe-statics", "-std=gnu++17"]

def compile_c(src, obj):
    cmd = [CC] + CFLAGS + [str(src), "-o", str(obj)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error compiling {src}:\n{res.stderr}")
        sys.exit(1)

def compile_cxx(src, obj):
    cmd = [CXX] + CXXFLAGS + [str(src), "-o", str(obj)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error compiling {src}:\n{res.stderr}")
        sys.exit(1)

def build():
    objects = []
    
    # Compile Arduino Core C files
    c_files = list(CORE.glob("*.c")) + [WIRE / "utility" / "twi.c"]
    for c_file in c_files:
        obj = BUILD_DIR / f"{c_file.stem}_c.o"
        print(f"Compiling {c_file.name}...")
        compile_c(c_file, obj)
        objects.append(obj)
        
    # Compile Arduino Core CPP files
    cpp_files = [f for f in CORE.glob("*.cpp") if f.name != "main.cpp"] + [WIRE / "Wire.cpp"]
    for cpp_file in cpp_files:
        obj = BUILD_DIR / f"{cpp_file.stem}_cpp.o"
        print(f"Compiling {cpp_file.name}...")
        compile_cxx(cpp_file, obj)
        objects.append(obj)
        
    # Compile diagnostic runner INO (as C++)
    ino_file = ROOT / "arduino" / "diagnostic_runner" / "diagnostic_runner.ino"
    ino_cpp = BUILD_DIR / "diagnostic_runner.cpp"
    
    # Wrap INO with Arduino.h include and main()
    ino_content = ino_file.read_text(encoding="utf-8")
    main_code = """
void initVariant() { }
int main(void) {
    init();
    initVariant();
    #if defined(USBCON)
    USBDevice.attach();
    #endif
    setup();
    for (;;) {
        loop();
        if (serialEventRun) serialEventRun();
    }
    return 0;
}
"""
    ino_cpp.write_text(ino_content + "\n" + main_code, encoding="utf-8")
    ino_obj = BUILD_DIR / "diagnostic_runner.o"
    print("Compiling diagnostic_runner...")
    compile_cxx(ino_cpp, ino_obj)
    objects.append(ino_obj)
    
    # Link ELF
    elf_file = BUILD_DIR / "diagnostic_runner.elf"
    print("Linking ELF...")
    link_cmd = [
        CXX, "-w", "-Os", "-g", "-fuse-linker-plugin",
        "-Wl,--gc-sections", "-mmcu=atmega328p",
        "-o", str(elf_file)
    ] + [str(o) for o in objects] + ["-lm"]
    
    res = subprocess.run(link_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Linking error:\n{res.stderr}")
        sys.exit(1)
        
    # Create HEX
    hex_file = ROOT / "arduino" / "diagnostic_runner" / "diagnostic_runner.hex"
    objcopy_cmd = [
        OBJCOPY, "-O", "ihex", "-R", ".eeprom",
        str(elf_file), str(hex_file)
    ]
    res = subprocess.run(objcopy_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Objcopy error:\n{res.stderr}")
        sys.exit(1)
        
    print(f"\nSUCCESS: Firmware compiled to {hex_file}")
    
    # Check size
    subprocess.run([SIZE, "-A", str(elf_file)])

if __name__ == "__main__":
    build()
