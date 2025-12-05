#!/usr/bin/env python3
"""
PIN IDENTIFIER - Systematically test and identify HAT control pins
Based on the working test_pins_cycle.py script

This script helps you:
1. Test individual pins to see their effect
2. Mark pins as identified for different functions
3. Save your findings to a file
4. Build a complete pin mapping for your HAT
"""
import sys
import os
import time
import json

# Add the lib directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))

# Simple GPIO-only version - EXACT copy from test_pins_cycle.py
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

# Orange Pi Zero 2W (H618) ACTUAL GPIO pins from WiringOP documentation
# These are the correct GPIO chip numbers for the 40-pin header

# Common GPIO pins likely used by HATs (from WiringOP pinout)
OPI_ZERO2W_GPIOS = [
    # Most likely HAT control pins (based on common RPi HAT usage)
    73,   # Pin 7  - PC9  (often used for control signals)
    70,   # Pin 11 - PC6  (often used for control signals)  
    69,   # Pin 13 - PC5  (often used for control signals)
    72,   # Pin 15 - PC8  (often used for control signals)
    79,   # Pin 16 - PC15 (often used for control signals)
    78,   # Pin 18 - PC14 (often used for control signals)
    71,   # Pin 22 - PC7  (often used for control signals)
    74,   # Pin 26 - PC10 (often used for control signals)
    65,   # Pin 27 - PC1  (often used for control signals)
]

# Extended list including more 40-pin header pins
OPI_ZERO2W_EXTENDED = [
    # Core control pins
    73, 70, 69, 72, 79, 78, 71, 74, 65,
    
    # SPI pins (for reference, though SPI uses different interface)
    230, 231, 232, 233,  # SCLK, MOSI, MISO, CE
    
    # I2C pins (for reference)
    228, 229,  # SCL, SDA
    
    # UART pins (for reference) 
    226, 227,  # TXD, RXD
    
    # Additional GPIO pins from the pinout
    272, 262, 234,  # PI16, PI6, PH10
]

# Start with the most likely HAT pins
ALL_PINS = OPI_ZERO2W_GPIOS

class PinIdentifier:
    def __init__(self):
        self.opi = SimpleOrangePi()
        self.working_pins = []
        self.current_pin_index = 0
        self.identified_pins = {}
        self.load_pin_map()
        self.setup_pins()
    
    def setup_pins(self):
        """Setup all pins - same method as test_pins_cycle.py"""
        print("Initializing simple GPIO library...")
        print(f"Testing {len(ALL_PINS)} GPIO pins...")
        print("Setting up pins as outputs...\n")
        
        for pin in ALL_PINS:
            try:
                self.opi.setup(pin, self.opi.OUT)
                self.working_pins.append(pin)
            except Exception as e:
                print(f"Could not setup pin {pin}: {e}")
        
        print(f"Successfully configured {len(self.working_pins)} pins\n")
    
    def load_pin_map(self):
        """Load previously identified pins"""
        try:
            with open('pin_mapping.json', 'r') as f:
                self.identified_pins = json.load(f)
            print("Loaded existing pin mapping:")
            for function, pin in self.identified_pins.items():
                print(f"  {function}: GPIO {pin}")
            print()
        except FileNotFoundError:
            print("No existing pin mapping found - starting fresh\n")
    
    def save_pin_map(self):
        """Save identified pins to file"""
        with open('pin_mapping.json', 'w') as f:
            json.dump(self.identified_pins, f, indent=2)
        print(f"Pin mapping saved to pin_mapping.json")
    
    def test_pin(self, pin, duration=2, pulse_count=5):
        """Test a specific pin with different patterns"""
        print(f"\n=== Testing GPIO {pin} ===")
        print("Watch your HAT for any changes...")
        
        # Pattern 1: Steady HIGH
        print(f"1. Setting GPIO {pin} HIGH for {duration} seconds...")
        self.opi.digital_write(pin, self.opi.HIGH)
        time.sleep(duration)
        self.opi.digital_write(pin, self.opi.LOW)
        
        input("Press Enter to continue to pulsing test...")
        
        # Pattern 2: Fast pulses
        print(f"2. Pulsing GPIO {pin} {pulse_count} times...")
        for i in range(pulse_count):
            self.opi.digital_write(pin, self.opi.HIGH)
            time.sleep(0.2)
            self.opi.digital_write(pin, self.opi.LOW)
            time.sleep(0.2)
        
        input("Press Enter to continue to slow pulse test...")
        
        # Pattern 3: Slow pulses
        print(f"3. Slow pulsing GPIO {pin} 3 times...")
        for i in range(3):
            self.opi.digital_write(pin, self.opi.HIGH)
            time.sleep(1)
            self.opi.digital_write(pin, self.opi.LOW)
            time.sleep(1)
    
    def identify_pin(self, pin, function):
        """Mark a pin as identified for a specific function"""
        self.identified_pins[function] = pin
        print(f"✓ GPIO {pin} identified as: {function}")
        self.save_pin_map()
    
    def show_menu(self):
        """Show the main menu"""
        print("\n" + "="*50)
        print("PIN IDENTIFIER MENU")
        print("="*50)
        
        if self.working_pins:
            current_pin = self.working_pins[self.current_pin_index]
            print(f"Current Pin: GPIO {current_pin} ({self.current_pin_index + 1}/{len(self.working_pins)})")
            print(f"Available pins: {self.working_pins}")
        
        print("\nNavigation:")
        print("  n - Next pin")
        print("  p - Previous pin")
        print("  g - Go to specific pin number")
        print("  [number] - Jump directly to GPIO pin (e.g. '98')")
        
        print("\nTesting:")
        print("  t - Test current pin (recommended)")
        print("  q - Quick pulse current pin")
        print("  h - Hold current pin HIGH")
        print("  l - Set current pin LOW")
        print("  a - Test ALL pins in sequence (like original script)")
        print("  e - Expand to test more pins (if current set doesn't work)")
        
        print("\nIdentification:")
        print("  i - Identify current pin (mark its function)")
        print("  s - Show identified pins")
        print("  c - Clear pin identification")
        
        print("\nOther:")
        print("  x - Exit")
        print("="*50)
    
    def quick_test_all(self):
        """Quick test all pins like the original script"""
        print("Quick testing all pins (like test_pins_cycle.py)...")
        print("Watch for HAT activity!")
        
        for i, pin in enumerate(self.working_pins):
            try:
                self.opi.digital_write(pin, self.opi.HIGH)
                print(f"GPIO {pin} = HIGH (pin {i+1}/{len(self.working_pins)})", end='                    \r')
                time.sleep(0.1)
                self.opi.digital_write(pin, self.opi.LOW)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error with pin {pin}: {e}")
        print("\nQuick test complete!")
    
    def run(self):
        """Main program loop"""
        if len(self.working_pins) == 0:
            print("No pins available! Exiting...")
            return
        
        try:
            while True:
                self.show_menu()
                choice = input("\nEnter choice: ").lower().strip()
                
                if choice == 'x':
                    break
                elif choice == 'n':
                    self.current_pin_index = (self.current_pin_index + 1) % len(self.working_pins)
                elif choice == 'p':
                    self.current_pin_index = (self.current_pin_index - 1) % len(self.working_pins)
                elif choice == 'g':
                    try:
                        pin_num = int(input("Enter GPIO pin number: "))
                        if pin_num in self.working_pins:
                            self.current_pin_index = self.working_pins.index(pin_num)
                            print(f"✓ Switched to GPIO {pin_num}")
                        else:
                            print(f"❌ GPIO {pin_num} not available")
                            print(f"Available pins: {self.working_pins[:10]}...")  # Show first 10
                    except ValueError:
                        print("❌ Invalid pin number")
                    input("Press Enter to continue...")
                elif choice.isdigit():
                    # Allow direct pin number entry
                    try:
                        pin_num = int(choice)
                        if pin_num in self.working_pins:
                            self.current_pin_index = self.working_pins.index(pin_num)
                            print(f"✓ Switched to GPIO {pin_num}")
                        else:
                            print(f"❌ GPIO {pin_num} not available")
                            print(f"Available pins: {self.working_pins}")
                    except ValueError:
                        print("❌ Invalid choice")
                    input("Press Enter to continue...")
                elif choice == 't':
                    current_pin = self.working_pins[self.current_pin_index]
                    self.test_pin(current_pin)
                elif choice == 'q':
                    current_pin = self.working_pins[self.current_pin_index]
                    print(f"Quick pulsing GPIO {current_pin}...")
                    for _ in range(3):
                        self.opi.digital_write(current_pin, self.opi.HIGH)
                        time.sleep(0.2)
                        self.opi.digital_write(current_pin, self.opi.LOW)
                        time.sleep(0.2)
                elif choice == 'h':
                    current_pin = self.working_pins[self.current_pin_index]
                    self.opi.digital_write(current_pin, self.opi.HIGH)
                    print(f"GPIO {current_pin} set HIGH")
                elif choice == 'l':
                    current_pin = self.working_pins[self.current_pin_index]
                    self.opi.digital_write(current_pin, self.opi.LOW)
                    print(f"GPIO {current_pin} set LOW")
                elif choice == 'a':
                    self.quick_test_all()
                elif choice == 'e':
                    print("Expanding to test more GPIO pins...")
                    print("Adding extended Orange Pi Zero 2W pins to test list...")
                    
                    # Add the expanded pin list
                    expanded_pins = OPI_ZERO2W_EXTENDED
                    new_pins = []
                    
                    for pin in expanded_pins:
                        if pin not in self.working_pins:
                            try:
                                self.opi.setup(pin, self.opi.OUT)
                                self.working_pins.append(pin)
                                new_pins.append(pin)
                            except Exception as e:
                                pass
                    
                    if new_pins:
                        self.working_pins.sort()  # Keep pins in order
                        print(f"✓ Added {len(new_pins)} new pins: {new_pins}")
                    else:
                        print("No additional pins could be added")
                    
                    input("Press Enter to continue...")
                elif choice == 'i':
                    current_pin = self.working_pins[self.current_pin_index]
                    print("\nCommon HAT functions:")
                    print("  backlight - Backlight control")
                    print("  reset - Display reset")
                    print("  dc - Data/Command select")
                    print("  cs - Chip select")
                    print("  led1 - LED 1")
                    print("  led2 - LED 2") 
                    print("  button1 - Button 1")
                    print("  button2 - Button 2")
                    function = input("Enter function name (or custom): ").strip()
                    if function:
                        self.identify_pin(current_pin, function)
                elif choice == 's':
                    print("\nIdentified pins:")
                    if self.identified_pins:
                        for function, pin in self.identified_pins.items():
                            print(f"  {function}: GPIO {pin}")
                    else:
                        print("  No pins identified yet")
                elif choice == 'c':
                    if self.identified_pins:
                        print("Current identifications:")
                        for function, pin in self.identified_pins.items():
                            print(f"  {function}: GPIO {pin}")
                        confirm = input("Clear all identifications? (y/N): ").lower()
                        if confirm == 'y':
                            self.identified_pins = {}
                            self.save_pin_map()
                            print("All identifications cleared")
                    else:
                        print("No identifications to clear")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        
        finally:
            print("\nCleaning up...")
            # Turn all pins off - same as test_pins_cycle.py
            for pin in self.working_pins:
                try:
                    self.opi.digital_write(pin, self.opi.LOW)
                except:
                    pass
            
            self.opi.cleanup()
            print("Done!")

def main():
    print("=== GPIO PIN IDENTIFIER ===")
    print("Systematically identify HAT control pins")
    print("Based on working test_pins_cycle.py script\n")
    
    identifier = PinIdentifier()
    identifier.run()

if __name__ == "__main__":
    main()