"""
Custom GPIO pin control module for Orange Pi Zero 2W
Provides sysfs-based GPIO control as fallback when OPi.GPIO is not available
"""

import os
import time
from typing import Optional, Set

class PinController:
    """Sysfs-based GPIO control for Orange Pi Zero 2W"""
    
    def __init__(self):
        self.exported_pins: Set[int] = set()
        self.gpio_base_path = "/sys/class/gpio"
        
    def _write_file(self, filepath: str, value: str) -> bool:
        """Write value to a file safely"""
        try:
            with open(filepath, 'w') as f:
                f.write(str(value))
            return True
        except (IOError, OSError, PermissionError) as e:
            print(f"Error writing to {filepath}: {e}")
            return False
    
    def _read_file(self, filepath: str) -> Optional[str]:
        """Read value from a file safely"""
        try:
            with open(filepath, 'r') as f:
                return f.read().strip()
        except (IOError, OSError) as e:
            print(f"Error reading from {filepath}: {e}")
            return None
    
    def export_pin(self, gpio_num: int) -> bool:
        """Export a GPIO pin for user control"""
        if gpio_num in self.exported_pins:
            return True  # Already exported
            
        export_path = os.path.join(self.gpio_base_path, "export")
        if self._write_file(export_path, str(gpio_num)):
            # Wait a bit for the system to create the GPIO directory
            time.sleep(0.1)
            
            gpio_dir = os.path.join(self.gpio_base_path, f"gpio{gpio_num}")
            if os.path.exists(gpio_dir):
                self.exported_pins.add(gpio_num)
                return True
        return False
    
    def unexport_pin(self, gpio_num: int) -> bool:
        """Unexport a GPIO pin"""
        if gpio_num not in self.exported_pins:
            return True  # Already unexported
            
        unexport_path = os.path.join(self.gpio_base_path, "unexport")
        if self._write_file(unexport_path, str(gpio_num)):
            self.exported_pins.discard(gpio_num)
            return True
        return False
    
    def set_direction(self, gpio_num: int, direction: str) -> bool:
        """Set GPIO pin direction (in/out)"""
        if gpio_num not in self.exported_pins:
            return False
            
        direction_path = os.path.join(self.gpio_base_path, f"gpio{gpio_num}", "direction")
        return self._write_file(direction_path, direction)
    
    def setup_pin(self, gpio_num: int, direction: str = "out") -> bool:
        """Setup a pin (export + set direction)"""
        if self.export_pin(gpio_num):
            return self.set_direction(gpio_num, direction)
        return False
    
    def write_pin(self, gpio_num: int, value: int) -> bool:
        """Write value to GPIO pin (0 or 1)"""
        if gpio_num not in self.exported_pins:
            return False
            
        value_path = os.path.join(self.gpio_base_path, f"gpio{gpio_num}", "value")
        return self._write_file(value_path, str(value))
    
    def read_pin(self, gpio_num: int) -> Optional[int]:
        """Read value from GPIO pin"""
        if gpio_num not in self.exported_pins:
            return None
            
        value_path = os.path.join(self.gpio_base_path, f"gpio{gpio_num}", "value")
        value_str = self._read_file(value_path)
        if value_str is not None:
            try:
                return int(value_str)
            except ValueError:
                pass
        return None
    
    def cleanup_all(self) -> bool:
        """Cleanup all exported pins"""
        success = True
        for gpio_num in list(self.exported_pins):
            if not self.unexport_pin(gpio_num):
                success = False
        return success
    
    def is_exported(self, gpio_num: int) -> bool:
        """Check if a GPIO pin is exported"""
        return gpio_num in self.exported_pins
    
    def list_exported_pins(self) -> Set[int]:
        """Get list of currently exported pins"""
        return self.exported_pins.copy()