#!/usr/bin/env python3
"""
Advanced GPIO Pin Controller with additional features
Enhanced version with pattern testing, pin monitoring, and export functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import json
import csv
from datetime import datetime
from gpio_pin_controller import GPIOController, OPI_ZERO2W_PINOUT, init_gpio_library

class AdvancedGPIOController:
    """Advanced GPIO controller with pattern testing and monitoring"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Orange Pi Zero 2W GPIO Controller")
        self.root.geometry("1200x800")
        
        # Initialize GPIO
        if not init_gpio_library():
            messagebox.showerror("Error", "No GPIO library found!")
            return
            
        self.gpio_controller = GPIOController()
        self.monitoring_active = False
        self.pattern_active = False
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create the advanced GUI"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Basic Control
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Control")
        self.create_basic_control(basic_frame)
        
        # Tab 2: Pattern Testing
        pattern_frame = ttk.Frame(notebook)
        notebook.add(pattern_frame, text="Pattern Testing")
        self.create_pattern_testing(pattern_frame)
        
        # Tab 3: Monitoring
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="Pin Monitoring")
        self.create_monitoring(monitor_frame)
        
        # Tab 4: Configuration
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self.create_configuration(config_frame)
    
    def create_basic_control(self, parent):
        """Create basic pin control interface"""
        # Pin selection frame
        select_frame = tk.LabelFrame(parent, text="Pin Selection")
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Available GPIO pins
        gpio_pins = [pin for pin, info in OPI_ZERO2W_PINOUT.items() if info[2] == "gpio"]
        
        self.selected_pins = tk.Listbox(select_frame, selectmode=tk.MULTIPLE, height=6)
        for pin in sorted(gpio_pins):
            gpio_num, desc, _ = OPI_ZERO2W_PINOUT[pin]
            self.selected_pins.insert(tk.END, f"Pin {pin} - {desc} (GPIO {gpio_num})")
        self.selected_pins.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Control buttons
        btn_frame = tk.Frame(select_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        tk.Button(btn_frame, text="Select All", command=self.select_all_pins).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Clear Selection", command=self.clear_selection).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Setup Selected", command=self.setup_selected).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Set HIGH", command=self.set_selected_high).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Set LOW", command=self.set_selected_low).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Toggle Selected", command=self.toggle_selected).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Cleanup Selected", command=self.cleanup_selected).pack(fill=tk.X, pady=2)
        
        # Status display
        status_frame = tk.LabelFrame(parent, text="Pin Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_pattern_testing(self, parent):
        """Create pattern testing interface"""
        # Pattern controls
        control_frame = tk.LabelFrame(parent, text="Pattern Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Pattern selection
        tk.Label(control_frame, text="Pattern:").grid(row=0, column=0, sticky="w", padx=5)
        self.pattern_var = tk.StringVar(value="blink")
        pattern_combo = ttk.Combobox(control_frame, textvariable=self.pattern_var,
                                   values=["blink", "chase", "wave", "random", "custom"])
        pattern_combo.grid(row=0, column=1, sticky="w", padx=5)
        
        # Timing controls
        tk.Label(control_frame, text="Speed (ms):").grid(row=0, column=2, sticky="w", padx=5)
        self.speed_var = tk.IntVar(value=500)
        speed_spin = tk.Spinbox(control_frame, from_=50, to=5000, increment=50, 
                               textvariable=self.speed_var, width=8)
        speed_spin.grid(row=0, column=3, sticky="w", padx=5)
        
        # Pattern buttons
        tk.Button(control_frame, text="Start Pattern", command=self.start_pattern).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Stop Pattern", command=self.stop_pattern).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="Save Pattern", command=self.save_pattern).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(control_frame, text="Load Pattern", command=self.load_pattern).grid(row=1, column=3, padx=5, pady=5)
        
        # Pattern display
        display_frame = tk.LabelFrame(parent, text="Pattern Visualization")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.pattern_canvas = tk.Canvas(display_frame, height=200, bg="black")
        self.pattern_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_monitoring(self, parent):
        """Create pin monitoring interface"""
        # Monitoring controls
        control_frame = tk.LabelFrame(parent, text="Monitoring Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.monitor_active_var = tk.BooleanVar()
        tk.Checkbutton(control_frame, text="Enable Real-time Monitoring",
                      variable=self.monitor_active_var,
                      command=self.toggle_monitoring).pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="Update Rate:").pack(side=tk.LEFT, padx=5)
        self.monitor_rate_var = tk.IntVar(value=100)
        rate_spin = tk.Spinbox(control_frame, from_=50, to=1000, increment=50,
                              textvariable=self.monitor_rate_var, width=8)
        rate_spin.pack(side=tk.LEFT, padx=5)
        tk.Label(control_frame, text="ms").pack(side=tk.LEFT)
        
        tk.Button(control_frame, text="Export Log", command=self.export_log).pack(side=tk.RIGHT, padx=5)
        tk.Button(control_frame, text="Clear Log", command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        
        # Monitoring display
        display_frame = tk.LabelFrame(parent, text="Pin State Log")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for log display
        columns = ("Time", "Pin", "GPIO", "State", "Event")
        self.log_tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=100)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(display_frame, orient="vertical", command=self.log_tree.yview)
        h_scroll = ttk.Scrollbar(display_frame, orient="horizontal", command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack everything
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_configuration(self, parent):
        """Create configuration interface"""
        # GPIO library info
        info_frame = tk.LabelFrame(parent, text="System Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        from gpio_pin_controller import GPIO_MODE
        info_text = f"""
GPIO Library: {GPIO_MODE}
Platform: Orange Pi Zero 2W
Total Pins: 40 (27 controllable GPIO)
Voltage Levels: 3.3V logic, 5V power
"""
        tk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # Pin configuration
        config_frame = tk.LabelFrame(parent, text="Pin Configuration")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create configuration tree
        config_columns = ("Pin", "GPIO", "Description", "Type", "Status")
        self.config_tree = ttk.Treeview(config_frame, columns=config_columns, show="headings")
        
        for col in config_columns:
            self.config_tree.heading(col, text=col)
            self.config_tree.column(col, width=120)
        
        # Populate with pin information
        self.update_config_display()
        
        config_scroll = ttk.Scrollbar(config_frame, orient="vertical", command=self.config_tree.yview)
        self.config_tree.configure(yscrollcommand=config_scroll.set)
        
        self.config_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        config_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        tk.Button(config_frame, text="Refresh Status", 
                 command=self.update_config_display).pack(pady=5)
    
    def update_config_display(self):
        """Update the configuration display"""
        # Clear existing items
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)
        
        # Add pin information
        for pin_num in sorted(OPI_ZERO2W_PINOUT.keys()):
            gpio_num, desc, pin_type = OPI_ZERO2W_PINOUT[pin_num]
            
            if pin_type == "gpio":
                status = "Exported" if pin_num in self.gpio_controller.exported_pins else "Available"
            else:
                status = "Fixed"
                
            self.config_tree.insert("", tk.END, values=(
                f"Pin {pin_num}", 
                f"GPIO {gpio_num}" if gpio_num else "N/A",
                desc,
                pin_type.upper(),
                status
            ))
    
    def get_selected_pin_numbers(self):
        """Get list of selected pin numbers"""
        selected_indices = self.selected_pins.curselection()
        gpio_pins = [pin for pin, info in OPI_ZERO2W_PINOUT.items() if info[2] == "gpio"]
        return [sorted(gpio_pins)[i] for i in selected_indices]
    
    def select_all_pins(self):
        """Select all GPIO pins"""
        self.selected_pins.select_set(0, tk.END)
    
    def clear_selection(self):
        """Clear pin selection"""
        self.selected_pins.selection_clear(0, tk.END)
    
    def setup_selected(self):
        """Setup selected pins"""
        pins = self.get_selected_pin_numbers()
        for pin in pins:
            success = self.gpio_controller.setup_pin(pin, "out")
            self.log_status(f"Setup Pin {pin}: {'Success' if success else 'Failed'}")
        self.update_config_display()
    
    def set_selected_high(self):
        """Set selected pins to HIGH"""
        pins = self.get_selected_pin_numbers()
        for pin in pins:
            if pin in self.gpio_controller.exported_pins:
                success = self.gpio_controller.set_pin_high(pin)
                self.log_status(f"Set Pin {pin} HIGH: {'Success' if success else 'Failed'}")
    
    def set_selected_low(self):
        """Set selected pins to LOW"""
        pins = self.get_selected_pin_numbers()
        for pin in pins:
            if pin in self.gpio_controller.exported_pins:
                success = self.gpio_controller.set_pin_low(pin)
                self.log_status(f"Set Pin {pin} LOW: {'Success' if success else 'Failed'}")
    
    def toggle_selected(self):
        """Toggle selected pins"""
        pins = self.get_selected_pin_numbers()
        for pin in pins:
            if pin in self.gpio_controller.exported_pins:
                current_state = self.gpio_controller.pin_states.get(pin, "LOW")
                if current_state == "LOW":
                    success = self.gpio_controller.set_pin_high(pin)
                    self.log_status(f"Toggle Pin {pin} to HIGH: {'Success' if success else 'Failed'}")
                else:
                    success = self.gpio_controller.set_pin_low(pin)
                    self.log_status(f"Toggle Pin {pin} to LOW: {'Success' if success else 'Failed'}")
    
    def cleanup_selected(self):
        """Cleanup selected pins"""
        pins = self.get_selected_pin_numbers()
        for pin in pins:
            if pin in self.gpio_controller.exported_pins:
                self.gpio_controller.exported_pins.discard(pin)
                self.log_status(f"Cleanup Pin {pin}")
        self.update_config_display()
    
    def start_pattern(self):
        """Start pattern testing"""
        if self.pattern_active:
            return
            
        pattern_type = self.pattern_var.get()
        speed = self.speed_var.get()
        pins = self.get_selected_pin_numbers()
        
        if not pins:
            messagebox.showwarning("Warning", "No pins selected for pattern!")
            return
        
        # Setup pins if needed
        for pin in pins:
            if pin not in self.gpio_controller.exported_pins:
                self.gpio_controller.setup_pin(pin, "out")
        
        self.pattern_active = True
        self.pattern_thread = threading.Thread(
            target=self.run_pattern, 
            args=(pattern_type, speed, pins),
            daemon=True
        )
        self.pattern_thread.start()
        self.log_status(f"Started {pattern_type} pattern on pins {pins}")
    
    def stop_pattern(self):
        """Stop pattern testing"""
        self.pattern_active = False
        self.log_status("Pattern stopped")
    
    def run_pattern(self, pattern_type, speed, pins):
        """Run the specified pattern"""
        step = 0
        while self.pattern_active:
            try:
                if pattern_type == "blink":
                    # All pins blink together
                    state = step % 2
                    for pin in pins:
                        if state:
                            self.gpio_controller.set_pin_high(pin)
                        else:
                            self.gpio_controller.set_pin_low(pin)
                
                elif pattern_type == "chase":
                    # One pin at a time
                    active_pin = pins[step % len(pins)]
                    for pin in pins:
                        if pin == active_pin:
                            self.gpio_controller.set_pin_high(pin)
                        else:
                            self.gpio_controller.set_pin_low(pin)
                
                elif pattern_type == "wave":
                    # Wave effect
                    for i, pin in enumerate(pins):
                        phase = (step + i * 2) % 4
                        if phase < 2:
                            self.gpio_controller.set_pin_high(pin)
                        else:
                            self.gpio_controller.set_pin_low(pin)
                
                # Update visualization
                self.update_pattern_visualization(pins, step)
                
                step += 1
                time.sleep(speed / 1000.0)
                
            except Exception as e:
                self.log_status(f"Pattern error: {e}")
                break
    
    def update_pattern_visualization(self, pins, step):
        """Update pattern visualization on canvas"""
        if hasattr(self, 'pattern_canvas'):
            self.pattern_canvas.delete("all")
            canvas_width = self.pattern_canvas.winfo_width()
            canvas_height = self.pattern_canvas.winfo_height()
            
            if canvas_width > 1:  # Canvas is initialized
                pin_width = canvas_width // len(pins)
                for i, pin in enumerate(pins):
                    x = i * pin_width
                    state = self.gpio_controller.pin_states.get(pin, "LOW")
                    color = "yellow" if state == "HIGH" else "darkgray"
                    
                    self.pattern_canvas.create_rectangle(
                        x + 2, 20, x + pin_width - 2, canvas_height - 20,
                        fill=color, outline="white"
                    )
                    self.pattern_canvas.create_text(
                        x + pin_width // 2, canvas_height - 10,
                        text=str(pin), fill="white", font=("Arial", 8)
                    )
    
    def toggle_monitoring(self):
        """Toggle pin monitoring"""
        if self.monitor_active_var.get():
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start pin monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_pins, daemon=True)
        self.monitor_thread.start()
        self.log_status("Started pin monitoring")
    
    def stop_monitoring(self):
        """Stop pin monitoring"""
        self.monitoring_active = False
        self.log_status("Stopped pin monitoring")
    
    def monitor_pins(self):
        """Monitor pin states"""
        last_states = {}
        while self.monitoring_active:
            try:
                for pin in self.gpio_controller.exported_pins:
                    value = self.gpio_controller.read_pin(pin)
                    if value is not None:
                        state = "HIGH" if value else "LOW"
                        if pin not in last_states or last_states[pin] != state:
                            # State changed
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            gpio_num = OPI_ZERO2W_PINOUT[pin][0]
                            
                            # Add to log tree
                            self.log_tree.insert("", 0, values=(
                                timestamp, f"Pin {pin}", f"GPIO {gpio_num}", state, "Change"
                            ))
                            
                            # Keep only last 1000 entries
                            children = self.log_tree.get_children()
                            if len(children) > 1000:
                                self.log_tree.delete(children[-1])
                            
                            last_states[pin] = state
                
                time.sleep(self.monitor_rate_var.get() / 1000.0)
            except Exception as e:
                self.log_status(f"Monitor error: {e}")
                break
    
    def save_pattern(self):
        """Save current pattern configuration"""
        config = {
            "pattern": self.pattern_var.get(),
            "speed": self.speed_var.get(),
            "pins": self.get_selected_pin_numbers()
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_status(f"Pattern saved to {filename}")
    
    def load_pattern(self):
        """Load pattern configuration"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                self.pattern_var.set(config.get("pattern", "blink"))
                self.speed_var.set(config.get("speed", 500))
                
                # Select pins
                self.clear_selection()
                loaded_pins = config.get("pins", [])
                gpio_pins = [pin for pin, info in OPI_ZERO2W_PINOUT.items() if info[2] == "gpio"]
                for pin in loaded_pins:
                    if pin in gpio_pins:
                        index = sorted(gpio_pins).index(pin)
                        self.selected_pins.selection_set(index)
                
                self.log_status(f"Pattern loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load pattern: {e}")
    
    def export_log(self):
        """Export monitoring log to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow(["Time", "Pin", "GPIO", "State", "Event"])
                    
                    # Write data
                    for child in self.log_tree.get_children():
                        values = self.log_tree.item(child)["values"]
                        writer.writerow(values)
                
                self.log_status(f"Log exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export log: {e}")
    
    def clear_log(self):
        """Clear monitoring log"""
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        self.log_status("Log cleared")
    
    def log_status(self, message):
        """Log status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.status_text.insert(tk.END, log_entry)
        self.status_text.see(tk.END)
    
    def on_closing(self):
        """Handle application closing"""
        self.pattern_active = False
        self.monitoring_active = False
        self.gpio_controller.cleanup()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedGPIOController()
    app.run()