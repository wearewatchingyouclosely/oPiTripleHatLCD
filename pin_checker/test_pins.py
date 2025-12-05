#!/usr/bin/env python3
"""
Simple command-line GPIO pin tester for Orange Pi Zero 2W
Quick test script to verify GPIO functionality before using the GUI
"""

import sys
import time
import argparse
from gpio_pin_controller import init_gpio_library, GPIOController, OPI_ZERO2W_PINOUT

def test_pin(pin_num: int, duration: float = 1.0):
    """Test a single GPIO pin by toggling it"""
    
    # Check if pin is valid
    pin_info = OPI_ZERO2W_PINOUT.get(pin_num)
    if not pin_info or pin_info[2] != "gpio":
        print(f"❌ Pin {pin_num} is not a controllable GPIO pin")
        if pin_info:
            print(f"   Pin type: {pin_info[2]}, Description: {pin_info[1]}")
        return False
    
    gpio_num, description, _ = pin_info
    print(f"🔧 Testing Pin {pin_num} (GPIO {gpio_num} - {description})")
    
    # Initialize GPIO controller
    controller = GPIOController()
    
    try:
        # Setup pin
        print("   Setting up pin for output...")
        if not controller.setup_pin(pin_num, "out"):
            print(f"❌ Failed to setup pin {pin_num}")
            return False
        
        # Test HIGH
        print("   Setting pin HIGH...")
        if not controller.set_pin_high(pin_num):
            print(f"❌ Failed to set pin {pin_num} HIGH")
            return False
        
        # Read back value
        value = controller.read_pin(pin_num)
        print(f"   Pin value: {value} ({'HIGH' if value else 'LOW'})")
        time.sleep(duration)
        
        # Test LOW
        print("   Setting pin LOW...")
        if not controller.set_pin_low(pin_num):
            print(f"❌ Failed to set pin {pin_num} LOW")
            return False
        
        # Read back value
        value = controller.read_pin(pin_num)
        print(f"   Pin value: {value} ({'HIGH' if value else 'LOW'})")
        time.sleep(duration)
        
        print(f"✅ Pin {pin_num} test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing pin {pin_num}: {e}")
        return False
    finally:
        # Always cleanup
        controller.cleanup()

def list_gpio_pins():
    """List all available GPIO pins"""
    print("📍 Orange Pi Zero 2W GPIO Pins:")
    print("-" * 50)
    
    gpio_pins = []
    power_pins = []
    ground_pins = []
    
    for pin_num in sorted(OPI_ZERO2W_PINOUT.keys()):
        gpio_num, description, pin_type = OPI_ZERO2W_PINOUT[pin_num]
        
        if pin_type == "gpio":
            gpio_pins.append((pin_num, gpio_num, description))
        elif pin_type == "power":
            power_pins.append((pin_num, description))
        elif pin_type == "ground":
            ground_pins.append((pin_num, description))
    
    # Show GPIO pins
    print("🔧 Controllable GPIO Pins:")
    for pin_num, gpio_num, desc in gpio_pins:
        print(f"   Pin {pin_num:2d} → GPIO {gpio_num:3d} ({desc})")
    
    # Show power pins
    print("\n⚡ Power Pins (Fixed):")
    for pin_num, desc in power_pins:
        print(f"   Pin {pin_num:2d} → {desc}")
    
    # Show ground pins
    print("\n🌍 Ground Pins (Fixed):")
    for pin_num, desc in ground_pins:
        print(f"   Pin {pin_num:2d} → {desc}")
    
    print(f"\nTotal: {len(gpio_pins)} GPIO pins, {len(power_pins)} power pins, {len(ground_pins)} ground pins")

def test_multiple_pins(pins: list, duration: float = 0.5):
    """Test multiple pins in sequence"""
    print(f"🧪 Testing {len(pins)} pins with {duration}s delay...")
    
    success_count = 0
    for pin_num in pins:
        print(f"\n--- Testing Pin {pin_num} ---")
        if test_pin(pin_num, duration):
            success_count += 1
        time.sleep(0.2)  # Small delay between tests
    
    print(f"\n📊 Test Summary: {success_count}/{len(pins)} pins tested successfully")
    return success_count == len(pins)

def main():
    parser = argparse.ArgumentParser(description="Orange Pi Zero 2W GPIO Pin Tester")
    parser.add_argument("--pin", type=int, help="Test specific pin number")
    parser.add_argument("--pins", type=int, nargs="+", help="Test multiple pins")
    parser.add_argument("--list", action="store_true", help="List all GPIO pins")
    parser.add_argument("--duration", type=float, default=1.0, 
                       help="Duration to hold each state (seconds)")
    parser.add_argument("--quick", action="store_true", 
                       help="Quick test of common pins (7,11,13,15)")
    
    args = parser.parse_args()
    
    print("🍊 Orange Pi Zero 2W GPIO Pin Tester")
    print("=" * 40)
    
    # Initialize GPIO library
    if not init_gpio_library():
        print("❌ No GPIO library found!")
        print("Please install:")
        print("  - OPi.GPIO: pip install OPi.GPIO")
        print("  - Or ensure you're running on Orange Pi with proper permissions")
        sys.exit(1)
    
    from gpio_pin_controller import GPIO_MODE
    print(f"✅ Using GPIO library: {GPIO_MODE}")
    print()
    
    try:
        if args.list:
            list_gpio_pins()
        elif args.pin:
            test_pin(args.pin, args.duration)
        elif args.pins:
            test_multiple_pins(args.pins, args.duration)
        elif args.quick:
            # Test common pins used by many HATs
            common_pins = [7, 11, 13, 15, 16, 18, 22]
            print("🚀 Quick test of common GPIO pins...")
            test_multiple_pins(common_pins, 0.3)
        else:
            # Interactive mode
            print("🎮 Interactive Mode")
            print("Commands:")
            print("  'list' - Show all pins")
            print("  'test <pin>' - Test specific pin")
            print("  'quick' - Quick test common pins")
            print("  'quit' - Exit")
            print()
            
            while True:
                try:
                    cmd = input("gpio> ").strip().lower()
                    if cmd == "quit" or cmd == "exit":
                        break
                    elif cmd == "list":
                        list_gpio_pins()
                    elif cmd == "quick":
                        test_multiple_pins([7, 11, 13, 15, 16, 18, 22], 0.3)
                    elif cmd.startswith("test "):
                        try:
                            pin_num = int(cmd.split()[1])
                            test_pin(pin_num, args.duration)
                        except (ValueError, IndexError):
                            print("❌ Invalid pin number. Use: test <pin_number>")
                    elif cmd == "help":
                        print("Commands: list, test <pin>, quick, quit")
                    else:
                        print(f"❌ Unknown command: {cmd}")
                        print("Type 'help' for commands")
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                print()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()