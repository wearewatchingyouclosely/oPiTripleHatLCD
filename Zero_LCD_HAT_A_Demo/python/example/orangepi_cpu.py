#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Orange Pi Zero 2W CPU Monitor for dual LCD displays
# Updated for Orange Pi Zero 2W running Armbian

import os
import sys 
import time
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_0inch96
from lib import Gain_Param
from PIL import Image,ImageDraw,ImageFont
import re 
import math
import psutil  # Better cross-platform system monitoring

# Orange Pi Zero 2W dual display pin configuration:
# Display 0 (SPI1.0)
RST_0 = 11  # GPIO 11 
DC_0 = 12   # GPIO 12
BL_0 = 13   # GPIO 13
bus_0 = 1 
device_0 = 0 

# Display 1 (SPI1.1) - if available, otherwise use different GPIOs
RST_1 = 15  # GPIO 15
DC_1 = 16   # GPIO 16 
BL_1 = 18   # GPIO 18
bus_1 = 1 
device_1 = 1 

logging.basicConfig(level=logging.DEBUG)

def get_cpu_usage():
    """Get CPU usage percentage"""
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """Get memory usage information"""
    memory = psutil.virtual_memory()
    return {
        'percent': memory.percent,
        'used': memory.used / (1024**3),  # GB
        'total': memory.total / (1024**3)  # GB
    }

def get_disk_usage():
    """Get disk usage information"""
    disk = psutil.disk_usage('/')
    return {
        'percent': (disk.used / disk.total) * 100,
        'used': disk.used / (1024**3),  # GB
        'total': disk.total / (1024**3)  # GB
    }

def get_cpu_temp():
    """Get CPU temperature (Orange Pi specific)"""
    try:
        # Orange Pi thermal zones
        thermal_paths = [
            '/sys/class/thermal/thermal_zone0/temp',
            '/sys/class/thermal/thermal_zone1/temp'
        ]
        
        for path in thermal_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    temp = int(f.read().strip()) / 1000.0
                    return temp
        
        # Fallback: try psutil
        temps = psutil.sensors_temperatures()
        if temps:
            # Get first available temperature sensor
            for name, entries in temps.items():
                if entries:
                    return entries[0].current
        
        return None
    except:
        return None

def get_network_info():
    """Get network interface information"""
    try:
        # Get network interfaces
        interfaces = psutil.net_if_addrs()
        for interface, addrs in interfaces.items():
            if interface != 'lo':  # Skip loopback
                for addr in addrs:
                    if addr.family == 2:  # IPv4
                        return {'interface': interface, 'ip': addr.address}
        return {'interface': 'N/A', 'ip': 'N/A'}
    except:
        return {'interface': 'N/A', 'ip': 'N/A'}

try:
    print("Initializing Orange Pi Zero 2W dual LCD displays...")
    
    # Initialize displays
    disp_0 = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus_0, device_0), spi_freq=10000000, rst=RST_0, dc=DC_0, bl=BL_0, bl_freq=1000)
    
    # Try to initialize second display
    try:
        disp_1 = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus_1, device_1), spi_freq=10000000, rst=RST_1, dc=DC_1, bl=BL_1, bl_freq=1000)
        dual_display = True
        print("Dual display mode enabled")
    except:
        disp_1 = None
        dual_display = False
        print("Single display mode (second display not available)")

    # Initialize displays
    disp_0.Init()
    if dual_display:
        disp_1.Init()

    disp_0.clear()
    if dual_display:
        disp_1.clear()

    disp_0.bl_DutyCycle(100)
    if dual_display:
        disp_1.bl_DutyCycle(100)

    # Create images for drawing
    image0 = Image.new("RGB", (disp_0.width, disp_0.height), "BLACK")
    draw0 = ImageDraw.Draw(image0)
    
    if dual_display:
        image1 = Image.new("RGB", (disp_1.width, disp_1.height), "BLACK")
        draw1 = ImageDraw.Draw(image1)

    # Load fonts
    try:
        Font1 = ImageFont.truetype("../Font/Font00.ttf", 12)
        Font2 = ImageFont.truetype("../Font/Font00.ttf", 10)
    except:
        Font1 = ImageFont.load_default()
        Font2 = ImageFont.load_default()

    print("Starting monitoring loop... Press Ctrl+C to exit")
    
    while True:
        # Get system information
        cpu_percent = get_cpu_usage()
        memory = get_memory_usage()
        disk = get_disk_usage()
        cpu_temp = get_cpu_temp()
        network = get_network_info()
        
        # Display 0: CPU and Memory info
        image0 = Image.new("RGB", (disp_0.width, disp_0.height), "BLACK")
        draw0 = ImageDraw.Draw(image0)
        
        draw0.text((5, 2), "Orange Pi Zero 2W", font=Font1, fill="CYAN")
        draw0.text((5, 15), f"CPU: {cpu_percent:.1f}%", font=Font2, fill="GREEN" if cpu_percent < 70 else "YELLOW" if cpu_percent < 90 else "RED")
        draw0.text((5, 28), f"MEM: {memory['percent']:.1f}%", font=Font2, fill="GREEN" if memory['percent'] < 70 else "YELLOW" if memory['percent'] < 90 else "RED")
        
        if cpu_temp:
            temp_color = "GREEN" if cpu_temp < 60 else "YELLOW" if cpu_temp < 80 else "RED"
            draw0.text((5, 41), f"TEMP: {cpu_temp:.1f}C", font=Font2, fill=temp_color)
        else:
            draw0.text((5, 41), "TEMP: N/A", font=Font2, fill="GRAY")
            
        draw0.text((5, 54), f"NET: {network['interface']}", font=Font2, fill="BLUE")
        draw0.text((5, 67), network['ip'], font=Font2, fill="BLUE")
        
        disp_0.ShowImage(image0)
        
        if dual_display:
            # Display 1: Disk and additional info
            image1 = Image.new("RGB", (disp_1.width, disp_1.height), "BLACK")
            draw1 = ImageDraw.Draw(image1)
            
            draw1.text((5, 2), "System Status", font=Font1, fill="CYAN")
            draw1.text((5, 15), f"DISK: {disk['percent']:.1f}%", font=Font2, fill="GREEN" if disk['percent'] < 70 else "YELLOW" if disk['percent'] < 90 else "RED")
            draw1.text((5, 28), f"Used: {disk['used']:.1f}GB", font=Font2, fill="WHITE")
            draw1.text((5, 41), f"Free: {disk['total']-disk['used']:.1f}GB", font=Font2, fill="WHITE")
            
            # Show uptime
            uptime = time.time() - psutil.boot_time()
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            draw1.text((5, 54), f"UP: {hours}h {minutes}m", font=Font2, fill="MAGENTA")
            
            # Show current time
            current_time = time.strftime("%H:%M:%S")
            draw1.text((5, 67), current_time, font=Font2, fill="YELLOW")
            
            disp_1.ShowImage(image1)
        
        time.sleep(2)  # Update every 2 seconds

except KeyboardInterrupt:
    print("\nStopping monitoring...")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Install psutil: sudo pip3 install psutil")
    print("2. Make sure SPI is enabled")
    print("3. Run with sudo: sudo python3 orangepi_cpu.py")
    print("4. Check display connections")

finally:
    try:
        disp_0.module_exit()
        if dual_display and disp_1:
            disp_1.module_exit()
        print("Cleanup completed")
    except:
        pass