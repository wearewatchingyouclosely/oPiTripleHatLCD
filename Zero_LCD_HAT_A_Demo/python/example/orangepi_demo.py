#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Orange Pi Zero 2W LCD HAT Demo
# Updated for Orange Pi Zero 2W running Armbian with SPI enabled

import os
import sys 
import time
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_0inch96
from PIL import Image,ImageDraw,ImageFont

# Orange Pi Zero 2W pin configuration:
# Using Orange Pi Zero 2W GPIO pins (26-pin header)
# SPI1 is typically used as SPI0 might conflict with other devices
RST = 11  # GPIO 11 (Physical pin 26)
DC = 12   # GPIO 12 (Physical pin 32) 
BL = 13   # GPIO 13 (Physical pin 33)
bus = 1   # SPI1 bus
device = 0 # CE0
logging.basicConfig(level=logging.DEBUG)

try:
    print("Initializing Orange Pi Zero 2W LCD HAT...")
    print(f"Using SPI bus {bus}, device {device}")
    print(f"GPIO pins - RST: {RST}, DC: {DC}, BL: {BL}")
    
    # Display with hardware SPI:
    # Note: Don't create multiple displayer objects!
    disp = LCD_0inch96.LCD_0inch96(spi=SPI.SpiDev(bus, device), spi_freq=10000000, rst=RST, dc=DC, bl=BL)
    
    # Initialize library
    print("Initializing display...")
    disp.Init()
    
    # Clear display
    disp.clear()
    
    # Set the backlight to 100%
    disp.bl_DutyCycle(100)
    
    # Create blank image for drawing
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    
    print("Showing test image...")
    # Try to show demo image if it exists
    try:
        image = Image.open('../pic/LCD_0inch96.jpg')	
        disp.ShowImage(image)
        time.sleep(2)
    except FileNotFoundError:
        print("Demo image not found, skipping...")
    
    # Test drawing text
    try:
        Font1 = ImageFont.truetype("../Font/Font00.ttf", 25)
        Font2 = ImageFont.truetype("../Font/Font00.ttf", 15)
    except:
        # Fallback to default font if custom fonts not available
        Font1 = ImageFont.load_default()
        Font2 = ImageFont.load_default()
    
    print("Drawing text...")
    draw.rectangle((0, 0, disp.width, disp.height), fill="BLACK")
    draw.text((5, 10), 'Orange Pi Zero 2W', font=Font1, fill="CYAN")
    draw.text((15, 35), 'LCD HAT Demo', font=Font2, fill="YELLOW")
    draw.text((20, 55), 'SPI Working!', font=Font2, fill="GREEN")
    
    disp.ShowImage(image1)
    time.sleep(3)
    
    # Test different colors
    print("Testing colors...")
    colors = ["RED", "GREEN", "BLUE", "YELLOW", "MAGENTA", "CYAN"]
    for color in colors:
        image1 = Image.new("RGB", (disp.width, disp.height), color)
        draw = ImageDraw.Draw(image1)
        draw.text((20, 30), color, font=Font2, fill="BLACK" if color == "YELLOW" else "WHITE")
        disp.ShowImage(image1)
        time.sleep(0.5)
    
    print("Demo completed successfully!")
    disp.module_exit()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Make sure SPI is enabled: sudo orangepi-config -> System -> Hardware -> spi-spidev")
    print("2. Install required packages: sudo apt install python3-pil python3-spidev")
    print("3. Install Orange Pi GPIO: sudo pip3 install OPi.GPIO")
    print("4. Run with sudo: sudo python3 orangepi_demo.py")
    print("5. Check if /dev/spidev1.0 exists")
    
    try:
        disp.module_exit()
    except:
        pass