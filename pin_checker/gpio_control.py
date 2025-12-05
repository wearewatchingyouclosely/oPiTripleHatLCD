#!/usr/bin/env python3
"""
Simple GPIO Control Tool for Orange Pi Zero 2W
Easy-to-use CLI for controlling GPIO pins individually or in groups
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Orange Pi Zero 2W GPIO pin mapping (Physical Pin -> GPIO Number)
# Based on H618 SoC and recent community research
ORANGEPI_ZERO2W_PINOUT = {
    3: 264,   # SDA.1
    5: 263,   # SCL.1  
    7: 269,   # PWM3
    8: 224,   # TXD.0
    10: 225,  # RXD.0
    11: 226,  # TXD.5
    12: 257,  # PI01
    13: 227,  # RXD.5
    15: 261,  # TXD.2
    16: 270,  # PWM4
    18: 228,  # PH04
    19: 231,  # MOSI.1
    21: 232,  # MISO.1
    22: 262,  # RXD.2
    23: 230,  # SCLK.1
    24: 229,  # CE.0
    26: 233,  # CE.1
    27: 266,  # SDA.2
    28: 265,  # SCL.2
    29: 256,  # PI00
    31: 271,  # PI15
    32: 267,  # PWM1
    33: 268,  # PI12
    35: 258,  # PI02
    36: 76,   # PC12
    37: 272,  # PI16
    38: 260,  # PI04
    40: 259   # PI03
}

# Power/Ground pins that should not be controlled
POWER_PINS = [1, 2, 4, 6, 9, 14, 17, 20, 25, 30, 34, 39]

class GPIOController:
    """Simple GPIO controller using sysfs interface"""
    
    def __init__(self):
        self.exported_pins = set()
        
    def export_pin(self, gpio_num):
        """Export a GPIO pin for use"""
        try:
            if gpio_num in self.exported_pins:
                return True
                
            with open("/sys/class/gpio/export", "w") as f:
                f.write(str(gpio_num))
            self.exported_pins.add(gpio_num)
            time.sleep(0.1)  # Give system time to create files
            return True
        except (PermissionError, OSError) as e:
            if "Device or resource busy" in str(e):
                # Pin already exported by another process
                self.exported_pins.add(gpio_num)
                return True
            return False
            
    def set_direction(self, gpio_num, direction):
        """Set pin direction (in/out)"""
        try:
            direction_path = f"/sys/class/gpio/gpio{gpio_num}/direction"
            if not os.path.exists(direction_path):
                return False
            with open(direction_path, "w") as f:
                f.write(direction)
            return True
        except (PermissionError, OSError):
            return False
            
    def set_value(self, gpio_num, value):
        """Set pin value (0/1)"""
        try:
            value_path = f"/sys/class/gpio/gpio{gpio_num}/value"
            if not os.path.exists(value_path):
                return False
            with open(value_path, "w") as f:
                f.write(str(value))
            return True
        except (PermissionError, OSError):
            return False
            
    def get_value(self, gpio_num):
        """Read pin value"""
        try:
            value_path = f"/sys/class/gpio/gpio{gpio_num}/value"
            if not os.path.exists(value_path):
                return None
            with open(value_path, "r") as f:
                return int(f.read().strip())
        except (PermissionError, OSError, ValueError):
            return None
            
    def unexport_pin(self, gpio_num):
        """Unexport a GPIO pin"""
        try:
            with open("/sys/class/gpio/unexport", "w") as f:
                f.write(str(gpio_num))
            self.exported_pins.discard(gpio_num)
            return True
        except (PermissionError, OSError):
            return False
            
    def cleanup(self):
        """Clean up all exported pins"""
        for gpio_num in self.exported_pins.copy():
            self.unexport_pin(gpio_num)

def physical_to_gpio(pin):
    """Convert physical pin number to GPIO number"""
    if pin in POWER_PINS:
        raise ValueError(f"Pin {pin} is a power/ground pin and cannot be controlled")
    if pin not in ORANGEPI_ZERO2W_PINOUT:
        raise ValueError(f"Pin {pin} is not a valid GPIO pin")
    return ORANGEPI_ZERO2W_PINOUT[pin]

def show_pinout():
    """Display the Orange Pi Zero 2W pinout"""
    print("\n" + "="*60)
    print("🍊 ORANGE PI ZERO 2W GPIO PINOUT")
    print("="*60)
    print("Physical Pin → GPIO Number (Function)")
    print("-" * 40)
    
    for pin in sorted(ORANGEPI_ZERO2W_PINOUT.keys()):
        gpio = ORANGEPI_ZERO2W_PINOUT[pin]
        print(f"Pin {pin:2d} → GPIO {gpio:3d}")
    
    print(f"\nPower/Ground pins (not controllable): {POWER_PINS}")
    print("="*60)

def interactive_mode():
    """Interactive CLI mode for easy GPIO control"""
    gpio = GPIOController()
    print("\n🎮 INTERACTIVE GPIO CONTROL")
    print("Type 'help' for commands, 'quit' to exit")
    
    while True:
        try:
            cmd = input("\nGPIO> ").strip().lower()
            
            if cmd == 'quit' or cmd == 'exit':
                break
            elif cmd == 'help':
                print("\n📋 AVAILABLE COMMANDS:")
                print("  pinout              - Show pin layout")
                print("  set <pin> <0|1>     - Set pin HIGH(1) or LOW(0)")
                print("  read <pin>          - Read pin value")
                print("  on <pin>            - Set pin HIGH")
                print("  off <pin>           - Set pin LOW")
                print("  list                - List all controllable pins")
                print("  status              - Show status of exported pins")
                print("  cleanup             - Unexport all pins")
                print("  quit/exit           - Exit program")
                
            elif cmd == 'pinout':
                show_pinout()
                
            elif cmd == 'list':
                print("\n📍 CONTROLLABLE PINS:")
                for pin in sorted(ORANGEPI_ZERO2W_PINOUT.keys()):
                    print(f"Pin {pin}")
                    
            elif cmd == 'status':
                print(f"\n📊 EXPORTED PINS: {sorted(gpio.exported_pins) if gpio.exported_pins else 'None'}")
                
            elif cmd == 'cleanup':
                gpio.cleanup()
                print("✅ All pins cleaned up")
                
            elif cmd.startswith('set '):
                parts = cmd.split()
                if len(parts) != 3:
                    print("❌ Usage: set <pin> <0|1>")
                    continue
                    
                try:
                    pin = int(parts[1])
                    value = int(parts[2])
                    if value not in [0, 1]:
                        print("❌ Value must be 0 or 1")
                        continue
                        
                    gpio_num = physical_to_gpio(pin)
                    if gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "out") and gpio.set_value(gpio_num, value):
                        print(f"✅ Pin {pin} (GPIO {gpio_num}) set to {'HIGH' if value else 'LOW'}")
                    else:
                        print(f"❌ Failed to control pin {pin}")
                        
                except ValueError as e:
                    print(f"❌ {e}")
                    
            elif cmd.startswith('on '):
                try:
                    pin = int(cmd.split()[1])
                    gpio_num = physical_to_gpio(pin)
                    if gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "out") and gpio.set_value(gpio_num, 1):
                        print(f"✅ Pin {pin} (GPIO {gpio_num}) turned ON")
                    else:
                        print(f"❌ Failed to turn on pin {pin}")
                except (ValueError, IndexError) as e:
                    print(f"❌ Usage: on <pin>")
                    
            elif cmd.startswith('off '):
                try:
                    pin = int(cmd.split()[1])
                    gpio_num = physical_to_gpio(pin)
                    if gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "out") and gpio.set_value(gpio_num, 0):
                        print(f"✅ Pin {pin} (GPIO {gpio_num}) turned OFF")
                    else:
                        print(f"❌ Failed to turn off pin {pin}")
                except (ValueError, IndexError) as e:
                    print(f"❌ Usage: off <pin>")
                    
            elif cmd.startswith('read '):
                try:
                    pin = int(cmd.split()[1])
                    gpio_num = physical_to_gpio(pin)
                    if gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "in"):
                        value = gpio.get_value(gpio_num)
                        if value is not None:
                            print(f"📖 Pin {pin} (GPIO {gpio_num}) = {'HIGH' if value else 'LOW'} ({value})")
                        else:
                            print(f"❌ Failed to read pin {pin}")
                    else:
                        print(f"❌ Failed to setup pin {pin} for reading")
                except (ValueError, IndexError) as e:
                    print(f"❌ Usage: read <pin>")
                    
            elif cmd == '':
                continue
            else:
                print(f"❌ Unknown command: '{cmd}'. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    gpio.cleanup()
    print("✅ GPIO cleanup complete")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Simple GPIO Control Tool for Orange Pi Zero 2W",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s --set 18 1         # Set pin 18 HIGH
  %(prog)s --set 18 0         # Set pin 18 LOW
  %(prog)s --read 18          # Read pin 18 value
  %(prog)s --pinout           # Show pin layout
  %(prog)s --blink 18 5       # Blink pin 18 five times
        """
    )
    
    parser.add_argument('--set', nargs=2, metavar=('PIN', 'VALUE'), 
                       help='Set pin to HIGH(1) or LOW(0)')
    parser.add_argument('--read', type=int, metavar='PIN',
                       help='Read pin value')
    parser.add_argument('--on', type=int, metavar='PIN',
                       help='Turn pin ON (HIGH)')
    parser.add_argument('--off', type=int, metavar='PIN', 
                       help='Turn pin OFF (LOW)')
    parser.add_argument('--blink', nargs=2, metavar=('PIN', 'COUNT'),
                       help='Blink pin specified number of times')
    parser.add_argument('--pinout', action='store_true',
                       help='Show Orange Pi Zero 2W pinout')
    parser.add_argument('--list', action='store_true',
                       help='List all controllable pins')
    
    args = parser.parse_args()
    
    # Check if running on compatible system
    if not os.path.exists("/sys/class/gpio"):
        print("❌ Error: GPIO sysfs interface not found")
        print("   Make sure you're running on Orange Pi with GPIO support")
        sys.exit(1)
    
    gpio = GPIOController()
    
    try:
        if args.pinout:
            show_pinout()
        elif args.list:
            print("🍊 Orange Pi Zero 2W Controllable Pins:")
            for pin in sorted(ORANGEPI_ZERO2W_PINOUT.keys()):
                print(f"  Pin {pin}")
        elif args.set:
            pin = int(args.set[0])
            value = int(args.set[1])
            if value not in [0, 1]:
                print("❌ Value must be 0 or 1")
                sys.exit(1)
            gpio_num = physical_to_gpio(pin)
            if gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "out") and gpio.set_value(gpio_num, value):
                print(f"✅ Pin {pin} (GPIO {gpio_num}) set to {'HIGH' if value else 'LOW'}")
            else:
                print(f"❌ Failed to control pin {pin}")
                sys.exit(1)
        elif args.on:
            pin = args.on
            gpio_num = physical_to_gpio(pin)
            if gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "out") and gpio.set_value(gpio_num, 1):
                print(f"✅ Pin {pin} (GPIO {gpio_num}) turned ON")
            else:
                print(f"❌ Failed to turn on pin {pin}")
                sys.exit(1)
        elif args.off:
            pin = args.off
            gpio_num = physical_to_gpio(pin)
            if gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "out") and gpio.set_value(gpio_num, 0):
                print(f"✅ Pin {pin} (GPIO {gpio_num}) turned OFF")
            else:
                print(f"❌ Failed to turn off pin {pin}")
                sys.exit(1)
        elif args.read:
            pin = args.read
            gpio_num = physical_to_gpio(pin)
            if gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "in"):
                value = gpio.get_value(gpio_num)
                if value is not None:
                    print(f"📖 Pin {pin} (GPIO {gpio_num}) = {'HIGH' if value else 'LOW'} ({value})")
                else:
                    print(f"❌ Failed to read pin {pin}")
                    sys.exit(1)
            else:
                print(f"❌ Failed to setup pin {pin} for reading")
                sys.exit(1)
        elif args.blink:
            pin = int(args.blink[0])
            count = int(args.blink[1])
            gpio_num = physical_to_gpio(pin)
            if not (gpio.export_pin(gpio_num) and gpio.set_direction(gpio_num, "out")):
                print(f"❌ Failed to setup pin {pin}")
                sys.exit(1)
            
            print(f"🔄 Blinking pin {pin} (GPIO {gpio_num}) {count} times...")
            for i in range(count):
                gpio.set_value(gpio_num, 1)
                time.sleep(0.5)
                gpio.set_value(gpio_num, 0)
                time.sleep(0.5)
                print(f"  Blink {i+1}/{count}")
            print("✅ Blinking complete")
        else:
            # No arguments - enter interactive mode
            interactive_mode()
            
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    finally:
        gpio.cleanup()

if __name__ == "__main__":
    main()