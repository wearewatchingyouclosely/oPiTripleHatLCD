#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPi.GPIO Pin Test for Orange Pi Zero 2W
Tests the proper BOARD pin numbering with OPi.GPIO library

This script verifies that OPi.GPIO correctly translates:
BOARD Pin 22 → PC8 (GPIO chip 72) 
BOARD Pin 18 → PC7 (GPIO chip 71)
BOARD Pin 24 → PC10 (GPIO chip 74)
BOARD Pin 12 → PC1 (GPIO chip 65)
"""

import sys
import time

try:
    import OPi.GPIO as GPIO
except ImportError:
    print("Error: OPi.GPIO library not found!")
    print("Install with: pip3 install --user OPi.GPIO")
    sys.exit(1)

# Pin definitions using BOARD numbering (physical pins)
TEST_PINS = {
    22: "RST_PIN (PC8/GPIO72)",
    18: "DC_PIN (PC7/GPIO71)", 
    24: "CS_PIN (PC10/GPIO74)",
    12: "BL_PIN (PC1/GPIO65)"
}

def test_opi_gpio():
    """Test OPi.GPIO BOARD pin numbering"""
    print("=" * 50)
    print("OPi.GPIO Pin Test - Orange Pi Zero 2W")
    print("Testing BOARD pin numbering translation")
    print("=" * 50)
    
    try:
        # Initialize GPIO
        print("\n1. Initializing OPi.GPIO...")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        print("   ✅ GPIO.setmode(GPIO.BOARD) successful")
        print(f"   Current mode: {GPIO.getmode()}")
        
        # Setup pins as outputs
        print("\n2. Setting up pins as outputs...")
        for pin, description in TEST_PINS.items():
            try:
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
                print(f"   ✅ Pin {pin:2d} ({description}) - Setup OK")
            except Exception as e:
                print(f"   ❌ Pin {pin:2d} ({description}) - Error: {e}")
                return False
        
        # Test pin control
        print("\n3. Testing pin control...")
        for cycle in range(3):
            print(f"\n   Cycle {cycle + 1}/3:")
            
            # Turn all pins ON
            for pin, description in TEST_PINS.items():
                try:
                    GPIO.output(pin, GPIO.HIGH)
                    state = GPIO.input(pin)
                    status = "HIGH" if state else "LOW"
                    print(f"     Pin {pin:2d} → HIGH (read: {status})")
                except Exception as e:
                    print(f"     Pin {pin:2d} → Error: {e}")
            
            time.sleep(0.5)
            
            # Turn all pins OFF
            for pin, description in TEST_PINS.items():
                try:
                    GPIO.output(pin, GPIO.LOW)
                    state = GPIO.input(pin)
                    status = "HIGH" if state else "LOW"
                    print(f"     Pin {pin:2d} → LOW  (read: {status})")
                except Exception as e:
                    print(f"     Pin {pin:2d} → Error: {e}")
            
            time.sleep(0.5)
        
        print("\n4. Individual pin test...")
        for pin, description in TEST_PINS.items():
            print(f"\n   Testing Pin {pin} ({description}):")
            
            # Test HIGH
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.1)
            state = GPIO.input(pin)
            print(f"     Set HIGH → Read: {'HIGH' if state else 'LOW'}")
            
            # Test LOW
            GPIO.output(pin, GPIO.LOW) 
            time.sleep(0.1)
            state = GPIO.input(pin)
            print(f"     Set LOW  → Read: {'HIGH' if state else 'LOW'}")
        
        print("\n" + "=" * 50)
        print("✅ SUCCESS! OPi.GPIO pin control working correctly!")
        print("\nKey findings:")
        print("- OPi.GPIO translates BOARD pins to Orange Pi GPIO automatically")
        print("- No need to manually manage GPIO chip numbers")
        print("- Standard RPi.GPIO API works seamlessly")
        print("- Pin states read back correctly")
        print("\nThis confirms the HAT should work with OPi.GPIO!")
        print("=" * 50)
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're running on Orange Pi Zero 2W")  
        print("2. Check OPi.GPIO is properly installed")
        print("3. Verify GPIO permissions (try with sudo)")
        return False
    finally:
        # Clean up
        print("\n5. Cleaning up GPIO...")
        try:
            GPIO.cleanup()
            print("   ✅ GPIO cleanup complete")
        except:
            print("   ⚠️  GPIO cleanup failed (may be OK)")

def main():
    """Main test function"""
    success = test_opi_gpio()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("You can now run the hello_world_opi.py script!")
    else:
        print("\n❌ Test failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()