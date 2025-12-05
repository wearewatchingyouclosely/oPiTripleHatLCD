#!/usr/bin/env python3
"""
Stress Testing and Validation Suite for Orange Pi Zero 2W GPIO
Comprehensive testing for reliability, timing, and edge cases
"""

import time
import threading
import statistics
import random
from datetime import datetime, timedelta
from gpio_pin_controller import GPIOController, OPI_ZERO2W_PINOUT, init_gpio_library

class GPIOStressTester:
    """Comprehensive GPIO stress testing suite"""
    
    def __init__(self):
        if not init_gpio_library():
            raise RuntimeError("No GPIO library found!")
        self.controller = GPIOController()
        self.test_results = {}
        
    def run_timing_test(self, pin, duration_seconds=10):
        """Test GPIO timing performance"""
        print(f"\n=== Timing Test: Pin {pin} ===")
        
        # Setup pin
        if not self.controller.setup_pin(pin, "out"):
            return {"error": "Failed to setup pin"}
        
        times = []
        iterations = 0
        start_time = time.time()
        
        try:
            while (time.time() - start_time) < duration_seconds:
                # Measure toggle timing
                toggle_start = time.perf_counter()
                self.controller.set_pin_high(pin)
                self.controller.set_pin_low(pin)
                toggle_end = time.perf_counter()
                
                times.append((toggle_end - toggle_start) * 1000)  # Convert to milliseconds
                iterations += 1
        
        except KeyboardInterrupt:
            print("Test interrupted by user")
        
        finally:
            self.controller.cleanup()
        
        if times:
            results = {
                "iterations": iterations,
                "duration": duration_seconds,
                "avg_time_ms": statistics.mean(times),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
                "frequency_hz": iterations / duration_seconds / 2  # /2 because we do HIGH+LOW per iteration
            }
            
            print(f"Iterations: {iterations}")
            print(f"Average toggle time: {results['avg_time_ms']:.3f} ms")
            print(f"Min/Max time: {results['min_time_ms']:.3f} / {results['max_time_ms']:.3f} ms")
            print(f"Standard deviation: {results['std_dev_ms']:.3f} ms")
            print(f"Effective frequency: {results['frequency_hz']:.1f} Hz")
            
            return results
        else:
            return {"error": "No timing data collected"}
    
    def run_reliability_test(self, pins, duration_minutes=5, pattern="toggle"):
        """Test GPIO reliability over extended period"""
        print(f"\n=== Reliability Test: {len(pins)} pins for {duration_minutes} minutes ===")
        
        # Setup all pins
        active_pins = []
        for pin in pins:
            if self.controller.setup_pin(pin, "out"):
                active_pins.append(pin)
                print(f"Pin {pin}: Setup OK")
            else:
                print(f"Pin {pin}: Setup FAILED")
        
        if not active_pins:
            return {"error": "No pins available for testing"}
        
        errors = 0
        operations = 0
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                for pin in active_pins:
                    try:
                        if pattern == "toggle":
                            success1 = self.controller.set_pin_high(pin)
                            success2 = self.controller.set_pin_low(pin)
                            if not (success1 and success2):
                                errors += 1
                            operations += 2
                        
                        elif pattern == "random":
                            if random.random() > 0.5:
                                success = self.controller.set_pin_high(pin)
                            else:
                                success = self.controller.set_pin_low(pin)
                            if not success:
                                errors += 1
                            operations += 1
                        
                        # Small delay to prevent overwhelming the system
                        time.sleep(0.001)
                        
                    except Exception as e:
                        print(f"Exception on pin {pin}: {e}")
                        errors += 1
                        
                    # Progress indicator
                    if operations % 10000 == 0:
                        elapsed = time.time() - start_time
                        remaining = end_time - time.time()
                        print(f"Progress: {elapsed/60:.1f}min elapsed, {remaining/60:.1f}min remaining, "
                              f"{operations} ops, {errors} errors")
        
        except KeyboardInterrupt:
            print("Test interrupted by user")
        
        finally:
            self.controller.cleanup()
        
        duration_actual = time.time() - start_time
        success_rate = ((operations - errors) / operations * 100) if operations > 0 else 0
        
        results = {
            "pins_tested": len(active_pins),
            "duration_seconds": duration_actual,
            "total_operations": operations,
            "errors": errors,
            "success_rate": success_rate,
            "ops_per_second": operations / duration_actual
        }
        
        print(f"\nReliability Test Results:")
        print(f"Pins tested: {len(active_pins)}")
        print(f"Duration: {duration_actual/60:.1f} minutes")
        print(f"Total operations: {operations}")
        print(f"Errors: {errors}")
        print(f"Success rate: {success_rate:.2f}%")
        print(f"Operations per second: {results['ops_per_second']:.1f}")
        
        return results
    
    def run_concurrent_test(self, pins, duration_seconds=30):
        """Test concurrent access to multiple pins"""
        print(f"\n=== Concurrent Access Test: {len(pins)} pins ===")
        
        # Setup pins
        setup_results = {}
        for pin in pins:
            setup_results[pin] = self.controller.setup_pin(pin, "out")
            print(f"Pin {pin}: {'Setup OK' if setup_results[pin] else 'Setup FAILED'}")
        
        active_pins = [pin for pin, success in setup_results.items() if success]
        if not active_pins:
            return {"error": "No pins available for testing"}
        
        # Shared test data
        test_data = {
            "start_time": time.time(),
            "end_time": time.time() + duration_seconds,
            "results": {pin: {"operations": 0, "errors": 0} for pin in active_pins},
            "lock": threading.Lock()
        }
        
        def pin_worker(pin):
            """Worker function for each pin"""
            while time.time() < test_data["end_time"]:
                try:
                    # Random operations
                    operation = random.choice(["high", "low", "toggle", "read"])
                    success = True
                    
                    if operation == "high":
                        success = self.controller.set_pin_high(pin)
                    elif operation == "low":
                        success = self.controller.set_pin_low(pin)
                    elif operation == "toggle":
                        current = self.controller.pin_states.get(pin, "LOW")
                        if current == "LOW":
                            success = self.controller.set_pin_high(pin)
                        else:
                            success = self.controller.set_pin_low(pin)
                    elif operation == "read":
                        value = self.controller.read_pin(pin)
                        success = value is not None
                    
                    # Update statistics
                    with test_data["lock"]:
                        test_data["results"][pin]["operations"] += 1
                        if not success:
                            test_data["results"][pin]["errors"] += 1
                    
                    # Small delay
                    time.sleep(0.005)
                    
                except Exception as e:
                    with test_data["lock"]:
                        test_data["results"][pin]["errors"] += 1
                    print(f"Exception in pin {pin} worker: {e}")
        
        # Start worker threads
        threads = []
        for pin in active_pins:
            thread = threading.Thread(target=pin_worker, args=(pin,), daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("Test interrupted by user")
        
        finally:
            self.controller.cleanup()
        
        # Calculate results
        total_ops = sum(data["operations"] for data in test_data["results"].values())
        total_errors = sum(data["errors"] for data in test_data["results"].values())
        duration_actual = time.time() - test_data["start_time"]
        
        results = {
            "pins_tested": len(active_pins),
            "duration_seconds": duration_actual,
            "total_operations": total_ops,
            "total_errors": total_errors,
            "success_rate": ((total_ops - total_errors) / total_ops * 100) if total_ops > 0 else 0,
            "ops_per_second": total_ops / duration_actual,
            "pin_details": test_data["results"]
        }
        
        print(f"\nConcurrent Test Results:")
        print(f"Duration: {duration_actual:.1f} seconds")
        print(f"Total operations: {total_ops}")
        print(f"Total errors: {total_errors}")
        print(f"Success rate: {results['success_rate']:.2f}%")
        print(f"Operations per second: {results['ops_per_second']:.1f}")
        
        for pin, data in test_data["results"].items():
            ops = data["operations"]
            errors = data["errors"]
            rate = ((ops - errors) / ops * 100) if ops > 0 else 0
            print(f"  Pin {pin}: {ops} ops, {errors} errors, {rate:.1f}% success")
        
        return results
    
    def run_memory_stress_test(self, duration_minutes=2):
        """Test for memory leaks during intensive GPIO operations"""
        print(f"\n=== Memory Stress Test: {duration_minutes} minutes ===")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        gpio_pins = [pin for pin, info in OPI_ZERO2W_PINOUT.items() if info[2] == "gpio"]
        test_pins = gpio_pins[:5]  # Use first 5 GPIO pins
        
        memory_samples = []
        operations = 0
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # Cycle through setup/use/cleanup
                for pin in test_pins:
                    # Setup
                    self.controller.setup_pin(pin, "out")
                    
                    # Use
                    for _ in range(50):
                        self.controller.set_pin_high(pin)
                        self.controller.set_pin_low(pin)
                        operations += 2
                    
                    # Sample memory every 1000 operations
                    if operations % 1000 == 0:
                        current_memory = process.memory_info().rss / 1024 / 1024
                        memory_samples.append({
                            "time": time.time() - start_time,
                            "memory_mb": current_memory,
                            "operations": operations
                        })
                        
                        if len(memory_samples) % 10 == 0:
                            print(f"Memory: {current_memory:.1f} MB, Operations: {operations}")
                
                # Cleanup all
                self.controller.cleanup()
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("Test interrupted by user")
        
        finally:
            self.controller.cleanup()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_delta = final_memory - initial_memory
        
        results = {
            "duration_minutes": (time.time() - start_time) / 60,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_delta_mb": memory_delta,
            "total_operations": operations,
            "memory_samples": memory_samples
        }
        
        print(f"\nMemory Stress Test Results:")
        print(f"Initial memory: {initial_memory:.1f} MB")
        print(f"Final memory: {final_memory:.1f} MB")
        print(f"Memory delta: {memory_delta:+.1f} MB")
        print(f"Total operations: {operations}")
        
        if memory_delta > 10:
            print("WARNING: Possible memory leak detected!")
        else:
            print("Memory usage looks stable")
        
        return results
    
    def run_edge_case_tests(self):
        """Test various edge cases and error conditions"""
        print("\n=== Edge Case Tests ===")
        
        results = {"tests": {}}
        
        # Test 1: Invalid pin numbers
        print("Testing invalid pin numbers...")
        invalid_pins = [0, 99, 41, -1, 1000]
        for pin in invalid_pins:
            success = self.controller.setup_pin(pin, "out")
            results["tests"][f"invalid_pin_{pin}"] = {
                "expected": False,
                "actual": success,
                "passed": not success
            }
        
        # Test 2: Double setup
        print("Testing double setup...")
        test_pin = 7  # Use pin 7 (GPIO 10)
        setup1 = self.controller.setup_pin(test_pin, "out")
        setup2 = self.controller.setup_pin(test_pin, "out")  # Should handle gracefully
        results["tests"]["double_setup"] = {
            "setup1": setup1,
            "setup2": setup2,
            "passed": setup1 and setup2  # Both should succeed
        }
        
        # Test 3: Operation on non-setup pin
        print("Testing operations on non-setup pins...")
        self.controller.cleanup()  # Ensure clean state
        non_setup_pin = 11
        set_result = self.controller.set_pin_high(non_setup_pin)
        read_result = self.controller.read_pin(non_setup_pin)
        results["tests"]["non_setup_operations"] = {
            "set_result": set_result,
            "read_result": read_result,
            "passed": not set_result and read_result is None
        }
        
        # Test 4: Rapid setup/cleanup cycles
        print("Testing rapid setup/cleanup...")
        rapid_errors = 0
        rapid_cycles = 100
        for i in range(rapid_cycles):
            try:
                if self.controller.setup_pin(test_pin, "out"):
                    self.controller.set_pin_high(test_pin)
                    self.controller.cleanup()
                else:
                    rapid_errors += 1
            except Exception:
                rapid_errors += 1
        
        results["tests"]["rapid_cycles"] = {
            "cycles": rapid_cycles,
            "errors": rapid_errors,
            "success_rate": (rapid_cycles - rapid_errors) / rapid_cycles * 100,
            "passed": rapid_errors < (rapid_cycles * 0.1)  # Less than 10% errors
        }
        
        # Test 5: Invalid directions
        print("Testing invalid pin directions...")
        invalid_dirs = ["input", "in", "output", "invalid", "", None, 123]
        invalid_dir_results = {}
        for direction in invalid_dirs:
            try:
                result = self.controller.setup_pin(test_pin, direction)
                invalid_dir_results[str(direction)] = {"result": result, "exception": False}
            except Exception as e:
                invalid_dir_results[str(direction)] = {"result": False, "exception": True}
        
        results["tests"]["invalid_directions"] = invalid_dir_results
        
        # Summary
        print(f"\nEdge Case Test Results:")
        passed_tests = sum(1 for test in results["tests"].values() 
                          if isinstance(test, dict) and test.get("passed", False))
        total_tests = len(results["tests"])
        
        print(f"Passed: {passed_tests}/{total_tests} tests")
        
        for test_name, test_data in results["tests"].items():
            if isinstance(test_data, dict) and "passed" in test_data:
                status = "PASS" if test_data["passed"] else "FAIL"
                print(f"  {test_name}: {status}")
        
        return results

def main():
    """Main test runner"""
    print("Orange Pi Zero 2W GPIO Stress Testing Suite")
    print("=" * 50)
    
    # Initialize tester
    try:
        tester = GPIOStressTester()
    except Exception as e:
        print(f"Failed to initialize tester: {e}")
        return
    
    # Available GPIO pins for testing
    gpio_pins = [pin for pin, info in OPI_ZERO2W_PINOUT.items() if info[2] == "gpio"]
    test_pins = gpio_pins[:3]  # Use first 3 pins for most tests
    
    print(f"Available GPIO pins: {gpio_pins}")
    print(f"Using pins for testing: {test_pins}")
    
    all_results = {}
    
    try:
        # Test menu
        while True:
            print("\n" + "=" * 50)
            print("GPIO Stress Test Menu:")
            print("1. Timing Test (single pin)")
            print("2. Reliability Test (multiple pins)")
            print("3. Concurrent Access Test")
            print("4. Memory Stress Test")
            print("5. Edge Case Tests")
            print("6. Run All Tests")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                pin = int(input(f"Enter pin number ({test_pins}): ") or test_pins[0])
                duration = int(input("Duration in seconds (default 10): ") or 10)
                all_results["timing"] = tester.run_timing_test(pin, duration)
                
            elif choice == "2":
                duration = int(input("Duration in minutes (default 2): ") or 2)
                pattern = input("Pattern (toggle/random, default toggle): ") or "toggle"
                all_results["reliability"] = tester.run_reliability_test(test_pins, duration, pattern)
                
            elif choice == "3":
                duration = int(input("Duration in seconds (default 30): ") or 30)
                all_results["concurrent"] = tester.run_concurrent_test(test_pins, duration)
                
            elif choice == "4":
                duration = int(input("Duration in minutes (default 2): ") or 2)
                all_results["memory"] = tester.run_memory_stress_test(duration)
                
            elif choice == "5":
                all_results["edge_cases"] = tester.run_edge_case_tests()
                
            elif choice == "6":
                print("Running all tests...")
                all_results["timing"] = tester.run_timing_test(test_pins[0], 5)
                all_results["reliability"] = tester.run_reliability_test(test_pins, 1, "toggle")
                all_results["concurrent"] = tester.run_concurrent_test(test_pins, 15)
                all_results["memory"] = tester.run_memory_stress_test(1)
                all_results["edge_cases"] = tester.run_edge_case_tests()
                
                print("\n" + "=" * 60)
                print("ALL TESTS COMPLETE - SUMMARY")
                print("=" * 60)
                
                for test_name, results in all_results.items():
                    print(f"\n{test_name.upper()}:")
                    if "error" in results:
                        print(f"  ERROR: {results['error']}")
                    elif "success_rate" in results:
                        print(f"  Success Rate: {results['success_rate']:.2f}%")
                    elif test_name == "timing" and "frequency_hz" in results:
                        print(f"  Max Frequency: {results['frequency_hz']:.1f} Hz")
                
            elif choice == "7":
                break
                
            else:
                print("Invalid choice, please try again.")
    
    except KeyboardInterrupt:
        print("\nTest suite interrupted by user")
    
    except Exception as e:
        print(f"Test suite error: {e}")
    
    finally:
        tester.controller.cleanup()
        print("GPIO cleanup complete")

if __name__ == "__main__":
    main()