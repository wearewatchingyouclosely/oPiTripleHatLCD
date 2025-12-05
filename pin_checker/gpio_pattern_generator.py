#!/usr/bin/env python3
"""
GPIO Pattern Generator and Sequencer
Create and run complex GPIO patterns for testing and demonstration
"""

import time
import json
import threading
from datetime import datetime
from gpio_pin_controller import GPIOController, OPI_ZERO2W_PINOUT, init_gpio_library

class GPIOPatternGenerator:
    """Generate and execute complex GPIO patterns"""
    
    def __init__(self):
        if not init_gpio_library():
            raise RuntimeError("No GPIO library found!")
        self.controller = GPIOController()
        self.patterns = {}
        self.active_sequence = None
        self.sequence_active = False
        
        # Load built-in patterns
        self.load_builtin_patterns()
    
    def load_builtin_patterns(self):
        """Load built-in demonstration patterns"""
        
        # Knight Rider pattern
        self.patterns["knight_rider"] = {
            "name": "Knight Rider",
            "description": "Back and forth scanning light",
            "pins": [7, 11, 13, 15, 16, 18, 19, 21],  # 8 pins in sequence
            "steps": [],
            "timing": 100  # milliseconds per step
        }
        
        # Generate knight rider steps
        pins = self.patterns["knight_rider"]["pins"]
        # Forward sweep
        for i in range(len(pins)):
            step = {pin: (1 if pin == pins[i] else 0) for pin in pins}
            self.patterns["knight_rider"]["steps"].append(step)
        # Reverse sweep (excluding endpoints to avoid double-flash)
        for i in range(len(pins) - 2, 0, -1):
            step = {pin: (1 if pin == pins[i] else 0) for pin in pins}
            self.patterns["knight_rider"]["steps"].append(step)
        
        # Binary Counter pattern
        self.patterns["binary_counter"] = {
            "name": "Binary Counter",
            "description": "Count in binary using GPIO pins",
            "pins": [7, 11, 13, 15],  # 4-bit counter
            "steps": [],
            "timing": 500
        }
        
        # Generate binary counter steps
        pins = self.patterns["binary_counter"]["pins"]
        for count in range(16):  # 0-15 in binary
            step = {}
            for i, pin in enumerate(pins):
                bit = (count >> i) & 1
                step[pin] = bit
            self.patterns["binary_counter"]["steps"].append(step)
        
        # Random Twinkle pattern
        self.patterns["random_twinkle"] = {
            "name": "Random Twinkle",
            "description": "Random twinkling lights",
            "pins": [7, 11, 13, 15, 16, 18, 19, 21, 23],
            "steps": [],
            "timing": 200,
            "random": True  # Special flag for random generation
        }
        
        # Traffic Light pattern
        self.patterns["traffic_light"] = {
            "name": "Traffic Light",
            "description": "Traffic light sequence (Red, Red+Yellow, Green, Yellow)",
            "pins": [7, 11, 13],  # Red, Yellow, Green
            "steps": [
                {7: 1, 11: 0, 13: 0},  # Red only
                {7: 1, 11: 1, 13: 0},  # Red + Yellow
                {7: 0, 11: 0, 13: 1},  # Green only
                {7: 0, 11: 1, 13: 0},  # Yellow only
            ],
            "timing": 1000  # 1 second per step
        }
        
        # Breathing pattern
        self.patterns["breathing"] = {
            "name": "Breathing",
            "description": "Gradual fade in/out effect (simulated with timing)",
            "pins": [7, 11, 13, 15, 16],
            "steps": [],
            "timing": 50,
            "pwm_simulation": True
        }
        
        # Generate breathing pattern (simulated PWM with rapid toggling)
        pins = self.patterns["breathing"]["pins"]
        for intensity in range(0, 11):  # 0 to 10
            # On phase
            for _ in range(intensity):
                step = {pin: 1 for pin in pins}
                self.patterns["breathing"]["steps"].append(step)
            # Off phase
            for _ in range(10 - intensity):
                step = {pin: 0 for pin in pins}
                self.patterns["breathing"]["steps"].append(step)
        
        # Reverse breathing
        for intensity in range(10, -1, -1):
            # On phase
            for _ in range(intensity):
                step = {pin: 1 for pin in pins}
                self.patterns["breathing"]["steps"].append(step)
            # Off phase
            for _ in range(10 - intensity):
                step = {pin: 0 for pin in pins}
                self.patterns["breathing"]["steps"].append(step)
    
    def create_custom_pattern(self, name, description, pins, steps, timing=100):
        """Create a custom pattern"""
        self.patterns[name] = {
            "name": name,
            "description": description,
            "pins": pins,
            "steps": steps,
            "timing": timing,
            "custom": True
        }
        return True
    
    def save_pattern_to_file(self, pattern_name, filename):
        """Save a pattern to JSON file"""
        if pattern_name not in self.patterns:
            return False
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.patterns[pattern_name], f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving pattern: {e}")
            return False
    
    def load_pattern_from_file(self, filename, pattern_name=None):
        """Load a pattern from JSON file"""
        try:
            with open(filename, 'r') as f:
                pattern_data = json.load(f)
            
            name = pattern_name or pattern_data.get("name", "loaded_pattern")
            self.patterns[name] = pattern_data
            return True
        except Exception as e:
            print(f"Error loading pattern: {e}")
            return False
    
    def list_patterns(self):
        """List all available patterns"""
        print("\nAvailable Patterns:")
        print("-" * 50)
        for key, pattern in self.patterns.items():
            print(f"{key:20} - {pattern['name']}")
            print(f"{'':20}   {pattern['description']}")
            print(f"{'':20}   Pins: {pattern['pins']}")
            print(f"{'':20}   Steps: {len(pattern['steps'])}, Timing: {pattern['timing']}ms")
            print()
    
    def run_pattern(self, pattern_name, repeat_count=1, setup_pins=True):
        """Run a specific pattern"""
        if pattern_name not in self.patterns:
            print(f"Pattern '{pattern_name}' not found!")
            return False
        
        pattern = self.patterns[pattern_name]
        pins = pattern["pins"]
        
        print(f"Running pattern: {pattern['name']}")
        print(f"Description: {pattern['description']}")
        print(f"Pins: {pins}")
        print(f"Duration per cycle: {len(pattern['steps']) * pattern['timing'] / 1000:.1f} seconds")
        
        # Setup pins if requested
        if setup_pins:
            for pin in pins:
                if not self.controller.setup_pin(pin, "out"):
                    print(f"Failed to setup pin {pin}")
                    return False
        
        try:
            for cycle in range(repeat_count):
                if repeat_count > 1:
                    print(f"Cycle {cycle + 1}/{repeat_count}")
                
                if pattern.get("random", False):
                    # Special handling for random patterns
                    self.run_random_pattern(pattern, pins)
                else:
                    # Normal step-by-step pattern
                    for step_num, step in enumerate(pattern["steps"]):
                        # Set all pins according to step
                        for pin in pins:
                            state = step.get(pin, 0)
                            if state:
                                self.controller.set_pin_high(pin)
                            else:
                                self.controller.set_pin_low(pin)
                        
                        # Wait for timing
                        time.sleep(pattern["timing"] / 1000.0)
                
                # Brief pause between cycles
                if cycle < repeat_count - 1:
                    time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\nPattern interrupted by user")
        
        except Exception as e:
            print(f"Error running pattern: {e}")
            return False
        
        finally:
            # Turn off all pins
            for pin in pins:
                self.controller.set_pin_low(pin)
        
        return True
    
    def run_random_pattern(self, pattern, pins):
        """Run a random twinkling pattern"""
        import random
        
        duration = 30  # 30 seconds of random twinkling
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            # Randomly select a few pins to light up
            num_active = random.randint(1, len(pins) // 2)
            active_pins = random.sample(pins, num_active)
            
            # Set pin states
            for pin in pins:
                if pin in active_pins:
                    self.controller.set_pin_high(pin)
                else:
                    self.controller.set_pin_low(pin)
            
            # Random timing
            delay = random.uniform(0.1, 0.5)
            time.sleep(delay)
    
    def create_sequence(self, sequence_name, pattern_list):
        """Create a sequence of patterns"""
        sequence = {
            "name": sequence_name,
            "patterns": [],
            "created": datetime.now().isoformat()
        }
        
        for item in pattern_list:
            if isinstance(item, str):
                # Simple pattern name
                if item in self.patterns:
                    sequence["patterns"].append({
                        "pattern": item,
                        "repeat": 1,
                        "pause": 1.0
                    })
            elif isinstance(item, dict):
                # Pattern with options
                if item.get("pattern") in self.patterns:
                    sequence["patterns"].append({
                        "pattern": item.get("pattern"),
                        "repeat": item.get("repeat", 1),
                        "pause": item.get("pause", 1.0)
                    })
        
        self.patterns[f"sequence_{sequence_name}"] = sequence
        return True
    
    def run_sequence(self, sequence_name):
        """Run a pattern sequence"""
        if sequence_name not in self.patterns:
            print(f"Sequence '{sequence_name}' not found!")
            return False
        
        sequence = self.patterns[sequence_name]
        if "patterns" not in sequence:
            print(f"'{sequence_name}' is not a valid sequence!")
            return False
        
        print(f"Running sequence: {sequence['name']}")
        print(f"Total patterns: {len(sequence['patterns'])}")
        
        self.sequence_active = True
        
        try:
            for i, pattern_config in enumerate(sequence["patterns"]):
                if not self.sequence_active:
                    break
                
                pattern_name = pattern_config["pattern"]
                repeat_count = pattern_config.get("repeat", 1)
                pause_duration = pattern_config.get("pause", 1.0)
                
                print(f"\nStep {i + 1}: {pattern_name} (repeat {repeat_count}x)")
                
                # Run the pattern
                self.run_pattern(pattern_name, repeat_count, setup_pins=(i == 0))
                
                # Pause between patterns
                if i < len(sequence["patterns"]) - 1 and pause_duration > 0:
                    print(f"Pausing for {pause_duration} seconds...")
                    time.sleep(pause_duration)
        
        except KeyboardInterrupt:
            print("\nSequence interrupted by user")
        
        finally:
            self.sequence_active = False
            self.controller.cleanup()
        
        return True
    
    def stop_sequence(self):
        """Stop the current sequence"""
        self.sequence_active = False
    
    def interactive_pattern_creator(self):
        """Interactive pattern creation tool"""
        print("\nInteractive Pattern Creator")
        print("-" * 30)
        
        # Get pattern info
        name = input("Pattern name: ").strip()
        if not name:
            print("Invalid name!")
            return False
        
        description = input("Description: ").strip() or "Custom pattern"
        
        # Get pins
        print("Available GPIO pins:", [pin for pin, info in OPI_ZERO2W_PINOUT.items() if info[2] == "gpio"])
        pin_input = input("Pins to use (comma-separated): ").strip()
        try:
            pins = [int(p.strip()) for p in pin_input.split(",")]
            # Validate pins
            valid_pins = [pin for pin, info in OPI_ZERO2W_PINOUT.items() if info[2] == "gpio"]
            pins = [pin for pin in pins if pin in valid_pins]
            if not pins:
                print("No valid pins specified!")
                return False
        except:
            print("Invalid pin format!")
            return False
        
        # Get timing
        try:
            timing = int(input("Timing per step (ms, default 200): ") or 200)
        except:
            timing = 200
        
        # Create steps interactively
        print(f"\nCreating steps for pins: {pins}")
        print("For each step, specify pin states (1=HIGH, 0=LOW)")
        print("Example: 1,0,1,0 for 4 pins")
        print("Enter 'done' when finished")
        
        steps = []
        step_num = 1
        
        while True:
            step_input = input(f"Step {step_num}: ").strip()
            
            if step_input.lower() == 'done':
                break
            
            try:
                states = [int(s.strip()) for s in step_input.split(",")]
                if len(states) != len(pins):
                    print(f"Must specify {len(pins)} states!")
                    continue
                
                step = {}
                for pin, state in zip(pins, states):
                    step[pin] = 1 if state else 0
                
                steps.append(step)
                step_num += 1
                
            except Exception as e:
                print(f"Invalid format: {e}")
        
        if not steps:
            print("No steps created!")
            return False
        
        # Create the pattern
        success = self.create_custom_pattern(name, description, pins, steps, timing)
        if success:
            print(f"\nPattern '{name}' created successfully!")
            print(f"Steps: {len(steps)}")
            print(f"Duration: {len(steps) * timing / 1000:.1f} seconds per cycle")
            
            # Ask to test
            if input("Test pattern now? (y/n): ").lower().startswith('y'):
                self.run_pattern(name)
            
            # Ask to save
            if input("Save pattern to file? (y/n): ").lower().startswith('y'):
                filename = input("Filename (default: pattern.json): ").strip() or "pattern.json"
                if self.save_pattern_to_file(name, filename):
                    print(f"Pattern saved to {filename}")
                else:
                    print("Failed to save pattern")
        
        return success

def main():
    """Main pattern generator interface"""
    print("Orange Pi Zero 2W GPIO Pattern Generator")
    print("=" * 50)
    
    try:
        generator = GPIOPatternGenerator()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
    
    while True:
        print("\n" + "=" * 50)
        print("GPIO Pattern Generator Menu:")
        print("1. List available patterns")
        print("2. Run a pattern")
        print("3. Create custom pattern (interactive)")
        print("4. Create pattern sequence")
        print("5. Run pattern sequence")
        print("6. Save pattern to file")
        print("7. Load pattern from file")
        print("8. Demo: Run all patterns")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        try:
            if choice == "1":
                generator.list_patterns()
                
            elif choice == "2":
                generator.list_patterns()
                pattern_name = input("Enter pattern name: ").strip()
                if pattern_name in generator.patterns:
                    repeat = int(input("Repeat count (default 1): ") or 1)
                    generator.run_pattern(pattern_name, repeat)
                else:
                    print("Pattern not found!")
            
            elif choice == "3":
                generator.interactive_pattern_creator()
            
            elif choice == "4":
                seq_name = input("Sequence name: ").strip()
                if not seq_name:
                    print("Invalid name!")
                    continue
                
                print("Available patterns:")
                for key in generator.patterns.keys():
                    if not key.startswith("sequence_"):
                        print(f"  {key}")
                
                pattern_list = []
                print("\nEnter patterns for sequence (one per line, 'done' to finish):")
                while True:
                    pattern = input("Pattern: ").strip()
                    if pattern.lower() == 'done':
                        break
                    if pattern in generator.patterns:
                        repeat = int(input(f"  Repeat count for {pattern} (default 1): ") or 1)
                        pause = float(input(f"  Pause after {pattern} (seconds, default 1): ") or 1)
                        pattern_list.append({
                            "pattern": pattern,
                            "repeat": repeat,
                            "pause": pause
                        })
                    else:
                        print(f"  Pattern '{pattern}' not found!")
                
                if pattern_list:
                    generator.create_sequence(seq_name, pattern_list)
                    print(f"Sequence '{seq_name}' created with {len(pattern_list)} patterns")
                else:
                    print("No valid patterns in sequence!")
            
            elif choice == "5":
                sequences = [key for key in generator.patterns.keys() if key.startswith("sequence_")]
                if sequences:
                    print("Available sequences:")
                    for seq in sequences:
                        print(f"  {seq}")
                    seq_name = input("Enter sequence name: ").strip()
                    generator.run_sequence(seq_name)
                else:
                    print("No sequences available!")
            
            elif choice == "6":
                generator.list_patterns()
                pattern_name = input("Pattern to save: ").strip()
                filename = input("Filename: ").strip()
                if pattern_name and filename:
                    if generator.save_pattern_to_file(pattern_name, filename):
                        print("Pattern saved successfully!")
                    else:
                        print("Failed to save pattern!")
            
            elif choice == "7":
                filename = input("Filename to load: ").strip()
                pattern_name = input("Pattern name (optional): ").strip() or None
                if generator.load_pattern_from_file(filename, pattern_name):
                    print("Pattern loaded successfully!")
                else:
                    print("Failed to load pattern!")
            
            elif choice == "8":
                print("Running demonstration of all patterns...")
                builtin_patterns = ["knight_rider", "binary_counter", "traffic_light", "random_twinkle"]
                for pattern_name in builtin_patterns:
                    if pattern_name in generator.patterns:
                        print(f"\nDemonstrating: {pattern_name}")
                        generator.run_pattern(pattern_name, 2)
                        time.sleep(2)
                        
            elif choice == "9":
                break
            
            else:
                print("Invalid choice!")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"Error: {e}")
    
    # Cleanup
    generator.controller.cleanup()
    print("GPIO cleanup complete")

if __name__ == "__main__":
    main()