#!/usr/bin/env python3
"""
Example Usage of Orange Pi Zero 2W GPIO Control Tool
Shows practical examples for common GPIO tasks
"""

import subprocess
import sys
import time
from pathlib import Path

def run_gpio_cmd(cmd_list):
    """Helper to run GPIO control commands"""
    script_path = Path(__file__).parent / "gpio_control.py"
    result = subprocess.run([sys.executable, str(script_path)] + cmd_list, 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ GPIO command failed: {result.stderr}")
        return False
    return True

def example_led_control():
    """Example: Simple LED control"""
    print("💡 Example 1: LED Control")
    print("-" * 30)
    print("Connect LED between pin 18 and ground (with resistor)")
    input("Press Enter when ready...")
    
    print("Turning LED on...")
    if run_gpio_cmd(["--on", "18"]):
        print("✅ LED should be ON")
    
    time.sleep(2)
    
    print("Turning LED off...")
    if run_gpio_cmd(["--off", "18"]):
        print("✅ LED should be OFF")

def example_button_reading():
    """Example: Button input reading"""
    print("\n🔘 Example 2: Button Reading")
    print("-" * 30)
    print("Connect button between pin 22 and ground")
    print("(Button pressed = LOW, released = HIGH with pull-up)")
    input("Press Enter when ready...")
    
    print("Reading button for 10 seconds (press and release)...")
    start_time = time.time()
    last_state = None
    
    while time.time() - start_time < 10:
        # Read button state
        result = subprocess.run([sys.executable, str(Path(__file__).parent / "gpio_control.py"), 
                               "--read", "22"], capture_output=True, text=True)
        
        if result.returncode == 0:
            if "LOW" in result.stdout and last_state != "pressed":
                print("🔽 Button PRESSED!")
                last_state = "pressed"
            elif "HIGH" in result.stdout and last_state != "released":
                print("🔼 Button RELEASED!")
                last_state = "released"
        
        time.sleep(0.1)

def example_pwm_simulation():
    """Example: Simulated PWM for LED dimming"""
    print("\n🌟 Example 3: LED Dimming (Simulated PWM)")
    print("-" * 30)
    print("Connect LED between pin 18 and ground (with resistor)")
    input("Press Enter when ready...")
    
    print("Dimming LED up and down...")
    
    # Brighten LED (faster switching)
    for duty in range(1, 10):
        for _ in range(20):
            run_gpio_cmd(["--on", "18"])
            time.sleep(duty * 0.001)  # ON time
            run_gpio_cmd(["--off", "18"])
            time.sleep((10-duty) * 0.001)  # OFF time
    
    # Dim LED (slower switching)
    for duty in range(10, 0, -1):
        for _ in range(20):
            run_gpio_cmd(["--on", "18"])
            time.sleep(duty * 0.001)
            run_gpio_cmd(["--off", "18"])
            time.sleep((10-duty) * 0.001)
    
    run_gpio_cmd(["--off", "18"])
    print("✅ Dimming complete")

def example_multiple_leds():
    """Example: Control multiple LEDs"""
    print("\n🎄 Example 4: Multiple LED Pattern")
    print("-" * 30)
    print("Connect LEDs to pins 18, 22, 24 (with resistors)")
    input("Press Enter when ready...")
    
    led_pins = [18, 22, 24]
    
    # Turn all off first
    for pin in led_pins:
        run_gpio_cmd(["--off", str(pin)])
    
    print("Running LED chase pattern...")
    for _ in range(5):
        for pin in led_pins:
            run_gpio_cmd(["--on", str(pin)])
            time.sleep(0.2)
            run_gpio_cmd(["--off", str(pin)])
    
    print("Running blink pattern...")
    for _ in range(3):
        # All on
        for pin in led_pins:
            run_gpio_cmd(["--on", str(pin)])
        time.sleep(0.5)
        
        # All off
        for pin in led_pins:
            run_gpio_cmd(["--off", str(pin)])
        time.sleep(0.5)
    
    print("✅ Pattern complete")

def example_hat_testing():
    """Example: Test Raspberry Pi HAT compatibility"""
    print("\n🎩 Example 5: HAT Compatibility Test")
    print("-" * 30)
    print("Connect your Raspberry Pi HAT to Orange Pi")
    input("Press Enter when ready...")
    
    # Common HAT pins to test
    hat_pins = {
        18: "GPIO24/SPI1_CE0",
        22: "GPIO25/SPI1_CE1", 
        24: "GPIO8/SPI0_CE0",
        26: "GPIO7/SPI0_CE1",
        12: "GPIO18/PWM0",
        16: "PWM4"
    }
    
    print("Testing HAT pins...")
    for pin, description in hat_pins.items():
        print(f"Testing pin {pin} ({description})")
        
        # Set as output and test
        if run_gpio_cmd(["--on", str(pin)]):
            time.sleep(0.1)
            if run_gpio_cmd(["--off", str(pin)]):
                print(f"  ✅ Pin {pin} working")
            else:
                print(f"  ❌ Pin {pin} cannot set LOW")
        else:
            print(f"  ❌ Pin {pin} cannot set HIGH")
        
        time.sleep(0.1)
    
    print("HAT compatibility test complete")

def example_script_integration():
    """Example: Using GPIO in shell scripts"""
    print("\n📝 Example 6: Shell Script Integration")
    print("-" * 30)
    
    script_content = '''#!/bin/bash
# Example bash script using GPIO control

echo "🚦 Traffic Light Demo"

# Red light
python3 gpio_control.py --on 18
echo "RED - Stop"
sleep 2

# Yellow light  
python3 gpio_control.py --off 18
python3 gpio_control.py --on 22
echo "YELLOW - Prepare"
sleep 1

# Green light
python3 gpio_control.py --off 22
python3 gpio_control.py --on 24
echo "GREEN - Go"
sleep 2

# All off
python3 gpio_control.py --off 24
echo "All lights off"
'''
    
    print("Example shell script:")
    print(script_content)
    
    create_script = input("Create and run this script? (y/N): ")
    if create_script.lower() == 'y':
        with open("/tmp/traffic_demo.sh", "w") as f:
            f.write(script_content)
        
        subprocess.run(["chmod", "+x", "/tmp/traffic_demo.sh"])
        print("Connect LEDs to pins 18(red), 22(yellow), 24(green)")
        input("Press Enter to run traffic light demo...")
        subprocess.run(["/tmp/traffic_demo.sh"])

def main():
    """Main example runner"""
    print("🍊 Orange Pi Zero 2W GPIO Examples")
    print("=" * 40)
    
    # Check if GPIO script exists
    script_path = Path(__file__).parent / "gpio_control.py"
    if not script_path.exists():
        print("❌ gpio_control.py not found!")
        print("   Run install.sh first")
        sys.exit(1)
    
    examples = [
        ("LED Control", example_led_control),
        ("Button Reading", example_button_reading),
        ("LED Dimming", example_pwm_simulation),
        ("Multiple LEDs", example_multiple_leds),
        ("HAT Testing", example_hat_testing),
        ("Script Integration", example_script_integration),
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. Run all examples")
    print("  q. Quit")
    
    while True:
        try:
            choice = input("\nChoose example (1-6, 0, q): ").strip()
            
            if choice.lower() == 'q':
                break
            elif choice == '0':
                for name, func in examples:
                    print(f"\n{'='*50}")
                    print(f"Running: {name}")
                    print('='*50)
                    try:
                        func()
                    except KeyboardInterrupt:
                        print("\n⏭️  Skipping to next example...")
                break
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(examples):
                    name, func = examples[idx]
                    print(f"\n{'='*50}")
                    print(f"Running: {name}")
                    print('='*50)
                    func()
                    break
                else:
                    print("❌ Invalid choice")
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Examples complete!")
    print("💡 Try interactive mode: python3 gpio_control.py")

if __name__ == "__main__":
    main()