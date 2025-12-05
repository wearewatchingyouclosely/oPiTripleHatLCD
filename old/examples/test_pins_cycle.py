#!/usr/bin/env python3
"""
Cycle through ALL available GPIO pins using the OrangePi GPIO library
Timing: 4 pins/sec for 5 cycles, then 2 pins/sec for 2 cycles, then 1 pin/sec indefinitely

DEPENDENCIES:
Before running this script, install required packages:

Debian/Ubuntu/Armbian:
  sudo apt update
  sudo apt install python3-pip python3-dev python3-spidev python3-numpy
  pip3 install spidev numpy

Windows (if testing on Windows):
  pip install spidev numpy
  
Orange Pi specific:
  # Enable SPI first:
  sudo armbian-config
  # Go to: System → Kernel → Select DTO001 (spi-spidev)
  # Reboot after enabling SPI
"""
import sys
import os
import time

# Add the lib directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))

# Simple GPIO-only version - no SPI needed for pin testing
class SimpleOrangePi:
    HIGH = 1
    LOW = 0
    OUT = "out"
    
    def __init__(self):
        self.setup_pins = []
    
    def setup(self, pin, direction):
        """Setup a GPIO pin"""
        try:
            # Export the pin
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(pin))
            time.sleep(0.01)
            
            # Set direction
            with open(f'/sys/class/gpio/gpio{pin}/direction', 'w') as f:
                f.write(direction)
            
            self.setup_pins.append(pin)
            return True
        except:
            return False
    
    def digital_write(self, pin, value):
        """Write HIGH or LOW to a pin"""
        try:
            with open(f'/sys/class/gpio/gpio{pin}/value', 'w') as f:
                f.write(str(value))
        except:
            pass
    
    def cleanup(self):
        """Clean up all pins"""
        for pin in self.setup_pins:
            try:
                # Turn off
                with open(f'/sys/class/gpio/gpio{pin}/value', 'w') as f:
                    f.write('0')
                # Unexport
                with open('/sys/class/gpio/unexport', 'w') as f:
                    f.write(str(pin))
            except:
                pass

# All UNCLAIMED GPIO pins from your pinmux output
ALL_PINS = [
    65, 69, 70, 71, 72, 73, 74, 75, 76, 78,  # PC1, PC5-12, PC14
    96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124,  # PD0-28
    128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150,  # PE0-22
    198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 211,  # PG6-19
    226, 227, 228, 229,  # PH2-5
    256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272  # PI0-16
]

def cycle_pins(pins, delay, cycles_info):
    """Cycle through pins with specified timing"""
    print(cycles_info)
    
    for cycle in range(len(pins) if cycles_info.startswith("indefinitely") else int(cycles_info.split()[0])):
        if not cycles_info.startswith("indefinitely"):
            print(f"  Cycle {cycle + 1}...")
        
        for i, pin in enumerate(pins):
            try:
                # Turn pin HIGH
                opi.digital_write(pin, opi.HIGH)
                print(f"GPIO {pin} = HIGH (pin {i+1}/{len(pins)})", end='                    \r')
                sys.stdout.flush()
                time.sleep(delay / 2)
                
                # Turn pin LOW
                opi.digital_write(pin, opi.LOW)
                time.sleep(delay / 2)
                
            except Exception as e:
                print(f"Error with pin {pin}: {e}")
                continue

# Initialize OrangePi
print("Initializing simple GPIO library...")
opi = SimpleOrangePi()

print(f"Testing {len(ALL_PINS)} GPIO pins...")
print("Watch for ANY change on the HAT (backlight, display activity, etc.)")
print("Press Ctrl+C to stop\n")

# Setup all pins as outputs
working_pins = []
for pin in ALL_PINS:
    try:
        opi.setup(pin, opi.OUT)
        working_pins.append(pin)
    except Exception as e:
        print(f"Could not setup pin {pin}: {e}")

print(f"Successfully configured {len(working_pins)} pins")
print("Starting timed cycles...\n")

try:
    # Phase 1: 10 pins per second for 5 cycles (0.1 seconds per pin)
    cycle_pins(working_pins, 0.1, "5 cycles at 10 pins/second")
    
    # Phase 2: 2 pins per second for 2 cycles (0.5 seconds per pin)  
    cycle_pins(working_pins, 0.5, "2 cycles at 2 pins/second")
    
    # Phase 3: 1 pin per second indefinitely (1.0 second per pin)
    cycle_pins(working_pins, 1.0, "indefinitely at 1 pin/second")
    
except KeyboardInterrupt:
    print("\n\nCleaning up...")
    # Turn all pins off using the library
    for pin in working_pins:
        try:
            opi.digital_write(pin, opi.LOW)
        except:
            pass
    
    # Cleanup using the library
    opi.cleanup()
    print("Done!")
    print("\nIf you saw any activity, note which GPIO number was displayed!")
