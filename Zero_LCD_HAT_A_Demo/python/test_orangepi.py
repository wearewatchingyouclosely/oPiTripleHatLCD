#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
Orange Pi Zero 2W LCD HAT Test Script
Quick verification that everything is set up correctly
"""

import sys
import os

def test_imports():
    """Test if required libraries can be imported"""
    print("=== Testing Library Imports ===")
    
    # Test SPI
    try:
        import spidev
        print("✓ spidev - OK")
    except ImportError:
        print("✗ spidev - MISSING (sudo apt install python3-spidev)")
        return False
    
    # Test PIL
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✓ PIL (Pillow) - OK")
    except ImportError:
        print("✗ PIL - MISSING (sudo apt install python3-pil)")
        return False
    
    # Test numpy
    try:
        import numpy as np
        print("✓ numpy - OK")
    except ImportError:
        print("✓ numpy - MISSING (sudo apt install python3-numpy)")
    
    # Test GPIO libraries
    gpio_found = False
    try:
        import OPi.GPIO as GPIO
        print("✓ OPi.GPIO - OK (PREFERRED for Orange Pi)")
        gpio_found = True
    except ImportError:
        print("✗ OPi.GPIO - MISSING (sudo pip3 install OPi.GPIO)")
    
    try:
        import RPi.GPIO as GPIO
        print("✓ RPi.GPIO - OK (fallback)")
        gpio_found = True
    except ImportError:
        print("✗ RPi.GPIO - MISSING")
    
    try:
        import gpiozero
        print("✓ gpiozero - OK (fallback)")
        gpio_found = True
    except ImportError:
        print("✗ gpiozero - MISSING")
    
    if not gpio_found:
        print("ERROR: No GPIO library found!")
        return False
    
    return True

def test_spi_devices():
    """Check if SPI devices are available"""
    print("\n=== Testing SPI Devices ===")
    
    spi_found = False
    for bus in range(3):
        for device in range(3):
            spi_path = f'/dev/spidev{bus}.{device}'
            if os.path.exists(spi_path):
                print(f"✓ Found SPI device: {spi_path}")
                spi_found = True
    
    if not spi_found:
        print("✗ No SPI devices found!")
        print("  Enable SPI with: sudo orangepi-config")
        print("  Go to System -> Hardware -> spi-spidev")
        return False
    
    return True

def test_platform_detection():
    """Test platform detection"""
    print("\n=== Platform Detection ===")
    
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        
        if 'Allwinner' in cpuinfo:
            print("✓ Orange Pi detected (Allwinner SoC)")
            print("  Recommended SPI: /dev/spidev1.0")
        elif 'BCM' in cpuinfo:
            print("✓ Raspberry Pi detected")
            print("  Recommended SPI: /dev/spidev0.0")
        else:
            print("? Unknown ARM platform")
            
    except Exception as e:
        print(f"✗ Could not detect platform: {e}")
        return False
    
    return True

def test_library_import():
    """Test importing our LCD library"""
    print("\n=== Testing LCD Library Import ===")
    
    try:
        sys.path.append('..')
        from lib import LCD_0inch96
        print("✓ LCD_0inch96 library - OK")
    except ImportError as e:
        print(f"✗ LCD_0inch96 library - FAILED: {e}")
        return False
    
    try:
        from lib import lcdconfig
        print("✓ lcdconfig library - OK")
    except ImportError as e:
        print(f"✗ lcdconfig library - FAILED: {e}")
        return False
    
    return True

def test_permissions():
    """Test if running with proper permissions"""
    print("\n=== Testing Permissions ===")
    
    if os.geteuid() != 0:
        print("⚠ Not running as root (sudo)")
        print("  GPIO access may be limited")
        print("  Run with: sudo python3 test_orangepi.py")
        return False
    else:
        print("✓ Running with root permissions")
        return True

def main():
    """Run all tests"""
    print("Orange Pi Zero 2W LCD HAT Test Script")
    print("====================================")
    
    tests = [
        test_imports,
        test_spi_devices,
        test_platform_detection,
        test_library_import,
        test_permissions
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("✓ All tests passed! Ready to run LCD demos.")
        print("\nNext steps:")
        print("  sudo python3 orangepi_demo.py")
        print("  sudo python3 orangepi_cpu.py")
    else:
        print("✗ Some tests failed. Check the output above.")
        print("\nTo fix issues:")
        print("  1. Run: sudo bash install_orangepi.sh")
        print("  2. Enable SPI: sudo orangepi-config")
        print("  3. Reboot the system")

if __name__ == "__main__":
    main()