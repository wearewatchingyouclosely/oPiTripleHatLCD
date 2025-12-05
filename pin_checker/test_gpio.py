#!/usr/bin/env python3
"""
GPIO Test Script for Orange Pi Zero 2W
Quick tests to verify GPIO functionality
"""

import sys
import time
import subprocess
from pathlib import Path

def run_gpio_command(cmd):
    """Run a GPIO control command and return result"""
    try:
        script_path = Path(__file__).parent / "gpio_control.py"
        result = subprocess.run([sys.executable, str(script_path)] + cmd, 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_basic_functionality():
    """Test basic GPIO operations"""
    print("🔧 Testing Basic GPIO Functionality...")
    print("-" * 40)
    
    # Test pinout command
    print("1. Testing pinout display...")
    success, stdout, stderr = run_gpio_command(["--pinout"])
    if success and "ORANGE PI ZERO 2W GPIO PINOUT" in stdout:
        print("   ✅ Pinout command works")
    else:
        print(f"   ❌ Pinout command failed: {stderr}")
        return False
    
    # Test list command
    print("2. Testing pin list...")
    success, stdout, stderr = run_gpio_command(["--list"])
    if success and "Pin " in stdout:
        print("   ✅ Pin list command works")
    else:
        print(f"   ❌ Pin list command failed: {stderr}")
        return False
    
    return True

def test_safe_pin_control():
    """Test GPIO pin control with safe pins"""
    print("\n🎮 Testing GPIO Pin Control...")
    print("-" * 40)
    
    # Use pin 18 as it's commonly safe to test
    test_pin = 18
    
    print(f"Testing pin {test_pin} (GPIO 228)...")
    
    # Test setting pin HIGH
    print("1. Setting pin HIGH...")
    success, stdout, stderr = run_gpio_command(["--on", str(test_pin)])
    if success:
        print("   ✅ Pin set HIGH")
    else:
        print(f"   ❌ Failed to set pin HIGH: {stderr}")
        return False
    
    time.sleep(0.5)
    
    # Test setting pin LOW
    print("2. Setting pin LOW...")
    success, stdout, stderr = run_gpio_command(["--off", str(test_pin)])
    if success:
        print("   ✅ Pin set LOW")
    else:
        print(f"   ❌ Failed to set pin LOW: {stderr}")
        return False
    
    # Test reading pin (set as input)
    print("3. Testing pin read...")
    success, stdout, stderr = run_gpio_command(["--read", str(test_pin)])
    if success:
        print(f"   ✅ Pin read successful: {stdout.strip()}")
    else:
        print(f"   ❌ Failed to read pin: {stderr}")
        return False
    
    return True

def test_blink():
    """Test blinking functionality"""
    print("\n💡 Testing Blink Function...")
    print("-" * 40)
    
    test_pin = 18
    blink_count = 2
    
    print(f"Blinking pin {test_pin} {blink_count} times...")
    success, stdout, stderr = run_gpio_command(["--blink", str(test_pin), str(blink_count)])
    
    if success and "Blinking complete" in stdout:
        print("   ✅ Blink test successful")
        return True
    else:
        print(f"   ❌ Blink test failed: {stderr}")
        return False

def check_permissions():
    """Check GPIO permissions"""
    print("🔒 Checking GPIO Permissions...")
    print("-" * 40)
    
    import os
    import grp
    
    # Check if GPIO directory exists
    if not os.path.exists("/sys/class/gpio"):
        print("   ❌ GPIO sysfs interface not found")
        return False
    else:
        print("   ✅ GPIO sysfs interface found")
    
    # Check if user is in gpio group
    try:
        gpio_gid = grp.getgrnam('gpio').gr_gid
        user_groups = os.getgroups()
        if gpio_gid in user_groups:
            print("   ✅ User is in GPIO group")
        else:
            print("   ⚠️  User is not in GPIO group (may need sudo)")
    except KeyError:
        print("   ⚠️  GPIO group does not exist")
    
    # Check write permissions on export file
    try:
        with open("/sys/class/gpio/export", "w") as f:
            pass
        print("   ✅ Can write to GPIO export")
        return True
    except PermissionError:
        print("   ❌ Cannot write to GPIO export (need sudo or gpio group)")
        return False
    except Exception as e:
        print(f"   ❌ GPIO export test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🍊 Orange Pi Zero 2W GPIO Test Suite")
    print("=" * 50)
    
    # Check if script exists
    script_path = Path(__file__).parent / "gpio_control.py"
    if not script_path.exists():
        print(f"❌ GPIO control script not found at {script_path}")
        print("   Run install.sh first!")
        sys.exit(1)
    
    print(f"Using GPIO script: {script_path}")
    print("")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    try:
        # Test 1: Permissions
        if check_permissions():
            tests_passed += 1
        
        print("")
        
        # Test 2: Basic functionality
        if test_basic_functionality():
            tests_passed += 1
        
        # Test 3: Pin control (only if we have permissions)
        if tests_passed >= 1:  # If we passed permission test
            if test_safe_pin_control():
                tests_passed += 1
            
            # Test 4: Blink function
            if test_blink():
                tests_passed += 1
        else:
            print("\n⚠️  Skipping pin control tests due to permission issues")
            print("   Try running with sudo or add user to gpio group")
    
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)
    
    # Results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("   Your GPIO setup is working correctly!")
        print("   Ready to control GPIO pins!")
    elif tests_passed >= 2:
        print("✅ MOSTLY WORKING!")
        print("   Basic functionality works, some advanced features may need attention")
    else:
        print("❌ ISSUES DETECTED!")
        print("   Check the error messages above")
        
        print("\n🛠️  TROUBLESHOOTING:")
        if tests_passed == 0:
            print("   • Make sure you're running on Orange Pi Zero 2W")
            print("   • Check if you need to add user to gpio group:")
            print("     sudo usermod -a -G gpio $USER")
            print("   • Try running with sudo:")
            print("     sudo python3 test_gpio.py")
        print("   • See README.md for more help")
    
    print("\n📖 Next steps:")
    print("   python3 gpio_control.py --help")
    print("   python3 gpio_control.py")

if __name__ == "__main__":
    main()