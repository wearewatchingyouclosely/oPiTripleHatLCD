#!/usr/bin/env python3
"""
Orange Pi Zero 2W GPIO Pin Controller
A GUI application for testing and controlling GPIO pins on Orange Pi Zero 2W

Features:
- Visual representation of 40-pin GPIO header
- Individual pin control (HIGH/LOW/INPUT)
- Bulk operations (set all, clear all)
- Pin state monitoring
- Safe pin management with proper cleanup

Author: GPIO Pin Controller
Compatible with: Orange Pi Zero 2W (H618)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import sys
import os
from datetime import datetime
from typing import Dict, Optional, Tuple

# GPIO Libraries - try multiple options for compatibility
GPIO_LIB = None
GPIO_MODE = None

def init_gpio_library():
    """Initialize the best available GPIO library"""
    global GPIO_LIB, GPIO_MODE
    
    # Try OPi.GPIO first (recommended)
    try:
        import OPi.GPIO as GPIO
        GPIO_LIB = GPIO
        GPIO_MODE = "OPi.GPIO"
        return True
    except ImportError:
        pass
    
    # Try custom sysfs control
    try:
        from pin_control import PinController
        GPIO_LIB = PinController()
        GPIO_MODE = "sysfs"
        return True
    except ImportError:
        pass
    
    return False

# Orange Pi Zero 2W pin mapping
# Physical pin number -> (GPIO number, description, pin type)
OPI_ZERO2W_PINOUT = {
    # Power pins (not controllable)
    1:  (None, "3.3V", "power"),
    2:  (None, "5V", "power"),
    4:  (None, "5V", "power"),
    6:  (None, "GND", "ground"),
    9:  (None, "GND", "ground"),
    14: (None, "GND", "ground"),
    17: (None, "3.3V", "power"),
    20: (None, "GND", "ground"),
    25: (None, "GND", "ground"),
    30: (None, "GND", "ground"),
    34: (None, "GND", "ground"),
    39: (None, "GND", "ground"),
    
    # GPIO pins (controllable)
    3:  (264, "SDA.1", "gpio"),
    5:  (263, "SCL.1", "gpio"),
    7:  (269, "PWM3", "gpio"),
    8:  (224, "TXD.0", "gpio"),
    10: (225, "RXD.0", "gpio"),
    11: (226, "TXD.5", "gpio"),
    12: (257, "PI01", "gpio"),
    13: (227, "RXD.5", "gpio"),
    15: (261, "TXD.2", "gpio"),
    16: (270, "PWM4", "gpio"),
    18: (228, "PH04", "gpio"),
    19: (231, "MOSI.1", "gpio"),
    21: (232, "MISO.1", "gpio"),
    22: (262, "RXD.2", "gpio"),
    23: (230, "SCLK.1", "gpio"),
    24: (229, "CE.0", "gpio"),
    26: (233, "CE.1", "gpio"),
    27: (266, "SDA.2", "gpio"),
    28: (265, "SCL.2", "gpio"),
    29: (256, "PI00", "gpio"),
    31: (271, "PI15", "gpio"),
    32: (267, "PWM1", "gpio"),
    33: (268, "PI12", "gpio"),
    35: (258, "PI02", "gpio"),
    36: (76, "PC12", "gpio"),
    37: (272, "PI16", "gpio"),
    38: (260, "PI04", "gpio"),
    40: (259, "PI03", "gpio"),
}

class GPIOController:
    """GPIO control wrapper supporting multiple libraries"""
    
    def __init__(self):
        self.exported_pins = set()
        self.pin_states = {}
        
    def setup_pin(self, pin_num: int, direction: str = "out") -> bool:
        """Setup a GPIO pin for input or output"""
        try:
            if GPIO_MODE == "OPi.GPIO":
                if not hasattr(self, '_gpio_initialized'):
                    GPIO_LIB.setmode(GPIO_LIB.BOARD)
                    GPIO_LIB.setwarnings(False)
                    self._gpio_initialized = True
                
                pin_info = OPI_ZERO2W_PINOUT.get(pin_num)
                if not pin_info or pin_info[2] != "gpio":
                    return False
                    
                if direction == "out":
                    GPIO_LIB.setup(pin_num, GPIO_LIB.OUT)
                else:
                    GPIO_LIB.setup(pin_num, GPIO_LIB.IN)
                    
                self.exported_pins.add(pin_num)
                return True
                
            elif GPIO_MODE == "sysfs":
                pin_info = OPI_ZERO2W_PINOUT.get(pin_num)
                if not pin_info or pin_info[2] != "gpio":
                    return False
                    
                gpio_num = pin_info[0]
                return GPIO_LIB.setup_pin(gpio_num, direction)
                
        except Exception as e:
            print(f"Error setting up pin {pin_num}: {e}")
            return False
            
        return False
    
    def set_pin_high(self, pin_num: int) -> bool:
        """Set pin to HIGH (3.3V)"""
        try:
            if GPIO_MODE == "OPi.GPIO":
                GPIO_LIB.output(pin_num, GPIO_LIB.HIGH)
                self.pin_states[pin_num] = "HIGH"
                return True
            elif GPIO_MODE == "sysfs":
                pin_info = OPI_ZERO2W_PINOUT.get(pin_num)
                if pin_info and pin_info[2] == "gpio":
                    success = GPIO_LIB.write_pin(pin_info[0], 1)
                    if success:
                        self.pin_states[pin_num] = "HIGH"
                    return success
        except Exception as e:
            print(f"Error setting pin {pin_num} HIGH: {e}")
        return False
    
    def set_pin_low(self, pin_num: int) -> bool:
        """Set pin to LOW (0V)"""
        try:
            if GPIO_MODE == "OPi.GPIO":
                GPIO_LIB.output(pin_num, GPIO_LIB.LOW)
                self.pin_states[pin_num] = "LOW"
                return True
            elif GPIO_MODE == "sysfs":
                pin_info = OPI_ZERO2W_PINOUT.get(pin_num)
                if pin_info and pin_info[2] == "gpio":
                    success = GPIO_LIB.write_pin(pin_info[0], 0)
                    if success:
                        self.pin_states[pin_num] = "LOW"
                    return success
        except Exception as e:
            print(f"Error setting pin {pin_num} LOW: {e}")
        return False
    
    def read_pin(self, pin_num: int) -> Optional[int]:
        """Read pin value (0 or 1)"""
        try:
            if GPIO_MODE == "OPi.GPIO":
                return GPIO_LIB.input(pin_num)
            elif GPIO_MODE == "sysfs":
                pin_info = OPI_ZERO2W_PINOUT.get(pin_num)
                if pin_info and pin_info[2] == "gpio":
                    return GPIO_LIB.read_pin(pin_info[0])
        except Exception as e:
            print(f"Error reading pin {pin_num}: {e}")
        return None
    
    def cleanup(self):
        """Clean up all GPIO resources"""
        try:
            if GPIO_MODE == "OPi.GPIO":
                GPIO_LIB.cleanup()
            elif GPIO_MODE == "sysfs":
                GPIO_LIB.cleanup_all()
            self.exported_pins.clear()
            self.pin_states.clear()
        except Exception as e:
            print(f"Error during cleanup: {e}")

class PinWidget(tk.Frame):
    """Widget representing a single GPIO pin"""
    
    def __init__(self, parent, pin_num: int, gpio_controller: GPIOController, 
                 log_callback=None):
        super().__init__(parent)
        self.pin_num = pin_num
        self.gpio_controller = gpio_controller
        self.log_callback = log_callback
        self.is_exported = False
        
        # Get pin information
        self.pin_info = OPI_ZERO2W_PINOUT.get(pin_num, (None, "Unknown", "unknown"))
        self.gpio_num, self.description, self.pin_type = self.pin_info
        
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        """Create the pin control widgets"""
        # Pin number label
        pin_label = tk.Label(self, text=f"Pin {self.pin_num}", 
                           font=("Arial", 8, "bold"))
        pin_label.pack()
        
        # Pin description
        desc_label = tk.Label(self, text=self.description, 
                            font=("Arial", 7))
        desc_label.pack()
        
        if self.pin_type == "gpio":
            # GPIO number
            gpio_label = tk.Label(self, text=f"GPIO {self.gpio_num}", 
                                font=("Arial", 6))
            gpio_label.pack()
            
            # Control buttons
            btn_frame = tk.Frame(self)
            btn_frame.pack(pady=2)
            
            self.setup_btn = tk.Button(btn_frame, text="Setup", 
                                     command=self.setup_pin, 
                                     font=("Arial", 6))
            self.setup_btn.pack(side=tk.LEFT, padx=1)
            
            self.high_btn = tk.Button(btn_frame, text="HIGH", 
                                    command=self.set_high,
                                    font=("Arial", 6), state=tk.DISABLED)
            self.high_btn.pack(side=tk.LEFT, padx=1)
            
            self.low_btn = tk.Button(btn_frame, text="LOW", 
                                   command=self.set_low,
                                   font=("Arial", 6), state=tk.DISABLED)
            self.low_btn.pack(side=tk.LEFT, padx=1)
            
            # State display
            self.state_label = tk.Label(self, text="Not Setup", 
                                      font=("Arial", 7), fg="gray")
            self.state_label.pack()
            
        elif self.pin_type in ["power", "ground"]:
            # Power/Ground pins - not controllable
            state_label = tk.Label(self, text="Fixed", 
                                 font=("Arial", 7), fg="blue")
            state_label.pack()
    
    def setup_pin(self):
        """Setup the pin for output"""
        if self.gpio_controller.setup_pin(self.pin_num, "out"):
            self.is_exported = True
            self.setup_btn.config(state=tk.DISABLED)
            self.high_btn.config(state=tk.NORMAL)
            self.low_btn.config(state=tk.NORMAL)
            self.state_label.config(text="Ready", fg="green")
            self.log(f"Pin {self.pin_num} (GPIO {self.gpio_num}) setup successful")
        else:
            self.log(f"Failed to setup pin {self.pin_num}")
    
    def set_high(self):
        """Set pin to HIGH"""
        if self.gpio_controller.set_pin_high(self.pin_num):
            self.state_label.config(text="HIGH", fg="red", bg="yellow")
            self.log(f"Pin {self.pin_num} set to HIGH")
        else:
            self.log(f"Failed to set pin {self.pin_num} HIGH")
    
    def set_low(self):
        """Set pin to LOW"""
        if self.gpio_controller.set_pin_low(self.pin_num):
            self.state_label.config(text="LOW", fg="blue", bg="white")
            self.log(f"Pin {self.pin_num} set to LOW")
        else:
            self.log(f"Failed to set pin {self.pin_num} LOW")
    
    def update_display(self):
        """Update the visual display based on pin type"""
        if self.pin_type == "power":
            self.config(bg="red", relief=tk.RAISED, bd=2)
        elif self.pin_type == "ground":
            self.config(bg="black", relief=tk.SUNKEN, bd=2)
        else:
            self.config(bg="lightgray", relief=tk.RAISED, bd=1)
    
    def log(self, message):
        """Send message to log callback"""
        if self.log_callback:
            self.log_callback(message)

class GPIOPinControllerGUI:
    """Main GUI application for GPIO pin control"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Orange Pi Zero 2W GPIO Pin Controller")
        self.root.geometry("1000x700")
        
        self.gpio_controller = GPIOController()
        self.pin_widgets = {}
        
        # Initialize GPIO library
        if not init_gpio_library():
            messagebox.showerror("Error", 
                               "No GPIO library found!\n"
                               "Please install OPi.GPIO or ensure you're running on Orange Pi.")
            sys.exit(1)
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        
        title_label = tk.Label(title_frame, 
                              text="Orange Pi Zero 2W GPIO Pin Controller",
                              font=("Arial", 16, "bold"))
        title_label.pack()
        
        info_label = tk.Label(title_frame, 
                             text=f"GPIO Library: {GPIO_MODE}",
                             font=("Arial", 10))
        info_label.pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # GPIO pins frame
        gpio_frame = tk.LabelFrame(content_frame, text="GPIO Header (40 pins)", 
                                  font=("Arial", 12, "bold"))
        gpio_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.create_pin_grid(gpio_frame)
        
        # Control panel
        control_frame = tk.LabelFrame(content_frame, text="Control Panel", 
                                    font=("Arial", 12, "bold"))
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        self.create_control_panel(control_frame)
    
    def create_pin_grid(self, parent):
        """Create the 40-pin GPIO header representation"""
        # Create two columns representing the physical GPIO header
        left_frame = tk.Frame(parent)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        right_frame = tk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Create pin widgets in pairs (odd pins on left, even on right)
        for row in range(20):  # 40 pins = 20 rows
            odd_pin = (row * 2) + 1
            even_pin = (row * 2) + 2
            
            # Left side (odd pins)
            pin_widget = PinWidget(left_frame, odd_pin, self.gpio_controller, 
                                 self.log_message)
            pin_widget.grid(row=row, column=0, padx=2, pady=1, sticky="ew")
            self.pin_widgets[odd_pin] = pin_widget
            
            # Right side (even pins)
            pin_widget = PinWidget(right_frame, even_pin, self.gpio_controller,
                                 self.log_message)
            pin_widget.grid(row=row, column=0, padx=2, pady=1, sticky="ew")
            self.pin_widgets[even_pin] = pin_widget
    
    def create_control_panel(self, parent):
        """Create the control panel with bulk operations"""
        # Bulk operations
        bulk_frame = tk.LabelFrame(parent, text="Bulk Operations")
        bulk_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(bulk_frame, text="Setup All GPIO Pins", 
                 command=self.setup_all_pins,
                 bg="green", fg="white").pack(fill=tk.X, pady=2)
        
        tk.Button(bulk_frame, text="Set All Pins HIGH", 
                 command=self.set_all_high,
                 bg="red", fg="white").pack(fill=tk.X, pady=2)
        
        tk.Button(bulk_frame, text="Set All Pins LOW", 
                 command=self.set_all_low,
                 bg="blue", fg="white").pack(fill=tk.X, pady=2)
        
        tk.Button(bulk_frame, text="Cleanup All Pins", 
                 command=self.cleanup_all,
                 bg="orange", fg="white").pack(fill=tk.X, pady=2)
        
        # Pin monitoring
        monitor_frame = tk.LabelFrame(parent, text="Monitoring")
        monitor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.monitor_var = tk.BooleanVar()
        monitor_check = tk.Checkbutton(monitor_frame, text="Real-time Pin Reading",
                                     variable=self.monitor_var,
                                     command=self.toggle_monitoring)
        monitor_check.pack()
        
        # Log frame
        log_frame = tk.LabelFrame(parent, text="Activity Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                font=("Consolas", 8))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear log button
        tk.Button(log_frame, text="Clear Log", 
                 command=self.clear_log).pack(pady=2)
        
        # Initial log message
        self.log_message(f"GPIO Pin Controller started with {GPIO_MODE}")
        self.log_message("Ready to control Orange Pi Zero 2W GPIO pins")
    
    def setup_all_pins(self):
        """Setup all GPIO pins for output"""
        count = 0
        for pin_num, pin_info in OPI_ZERO2W_PINOUT.items():
            if pin_info[2] == "gpio":
                widget = self.pin_widgets[pin_num]
                if not widget.is_exported:
                    widget.setup_pin()
                    count += 1
        self.log_message(f"Setup {count} GPIO pins")
    
    def set_all_high(self):
        """Set all exported GPIO pins to HIGH"""
        count = 0
        for pin_num, widget in self.pin_widgets.items():
            if hasattr(widget, 'is_exported') and widget.is_exported:
                widget.set_high()
                count += 1
        self.log_message(f"Set {count} pins to HIGH")
    
    def set_all_low(self):
        """Set all exported GPIO pins to LOW"""
        count = 0
        for pin_num, widget in self.pin_widgets.items():
            if hasattr(widget, 'is_exported') and widget.is_exported:
                widget.set_low()
                count += 1
        self.log_message(f"Set {count} pins to LOW")
    
    def cleanup_all(self):
        """Cleanup all GPIO resources"""
        self.gpio_controller.cleanup()
        for widget in self.pin_widgets.values():
            if hasattr(widget, 'is_exported'):
                widget.is_exported = False
                if hasattr(widget, 'setup_btn'):
                    widget.setup_btn.config(state=tk.NORMAL)
                    widget.high_btn.config(state=tk.DISABLED)
                    widget.low_btn.config(state=tk.DISABLED)
                    widget.state_label.config(text="Not Setup", fg="gray", bg="")
        self.log_message("All GPIO pins cleaned up")
    
    def toggle_monitoring(self):
        """Toggle real-time pin monitoring"""
        if self.monitor_var.get():
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_pins, daemon=True)
        self.monitor_thread.start()
        self.log_message("Started real-time monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.monitoring = False
        self.log_message("Stopped real-time monitoring")
    
    def monitor_pins(self):
        """Monitor pin states in background thread"""
        while self.monitoring:
            try:
                for pin_num, widget in self.pin_widgets.items():
                    if hasattr(widget, 'is_exported') and widget.is_exported:
                        value = self.gpio_controller.read_pin(pin_num)
                        if value is not None:
                            state = "HIGH" if value else "LOW"
                            if pin_num in self.gpio_controller.pin_states:
                                if self.gpio_controller.pin_states[pin_num] != state:
                                    self.log_message(f"Pin {pin_num} changed to {state}")
                                    self.gpio_controller.pin_states[pin_num] = state
                time.sleep(0.5)  # Update every 500ms
            except Exception as e:
                self.log_message(f"Monitor error: {e}")
                break
    
    def log_message(self, message):
        """Add message to the log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the activity log"""
        self.log_text.delete(1.0, tk.END)
    
    def on_closing(self):
        """Handle application closing"""
        if hasattr(self, 'monitoring'):
            self.monitoring = False
        self.gpio_controller.cleanup()
        self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

if __name__ == "__main__":
    app = GPIOPinControllerGUI()
    app.run()