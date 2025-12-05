# -*- coding: utf-8 -*-
"""
Orange Pi Zero 2W LCD Driver for Waveshare Zero LCD HAT (A)
Using OPi.GPIO library for proper GPIO control
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time

try:
    from . import lcdconfig_opi as config
except ImportError:
    import lcdconfig_opi as config

# Display constants
LCD_WIDTH = 160
LCD_HEIGHT = 80

class LCD_0inch96:
    """LCD driver for 0.96 inch 160x80 display"""
    
    def __init__(self):
        self.width = LCD_WIDTH
        self.height = LCD_HEIGHT
        
    def reset(self):
        """Hardware reset sequence"""
        print("Performing LCD reset...")
        config.digital_write(config.RST_PIN, 1)
        config.delay_ms(100)
        config.digital_write(config.RST_PIN, 0)
        config.delay_ms(100)
        config.digital_write(config.RST_PIN, 1)
        config.delay_ms(100)
        
    def write_command(self, cmd):
        """Send command to LCD"""
        config.digital_write(config.DC_PIN, 0)  # Command mode
        config.digital_write(config.CS_PIN, 0)  # Select device
        config.spi_writebyte(cmd)
        config.digital_write(config.CS_PIN, 1)  # Deselect device
        
    def write_data(self, data):
        """Send data to LCD"""
        config.digital_write(config.DC_PIN, 1)  # Data mode
        config.digital_write(config.CS_PIN, 0)  # Select device
        config.spi_writebyte(data)
        config.digital_write(config.CS_PIN, 1)  # Deselect device
        
    def write_data_bytes(self, data):
        """Send multiple data bytes to LCD"""
        config.digital_write(config.DC_PIN, 1)  # Data mode
        config.digital_write(config.CS_PIN, 0)  # Select device
        config.spi_writebytes(data)
        config.digital_write(config.CS_PIN, 1)  # Deselect device
        
    def init_lcd(self):
        """Initialize LCD with proper settings"""
        print("Initializing LCD...")
        
        # Initialize GPIO
        config.OPiGPIO.setup()
        
        # Hardware reset
        self.reset()
        
        # LCD initialization sequence for ST7735S
        print("Sending LCD initialization commands...")
        
        # Sleep out
        self.write_command(0x11)
        config.delay_ms(120)
        
        # Frame rate control
        self.write_command(0xB1)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)
        
        self.write_command(0xB2)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)
        
        self.write_command(0xB3)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)
        
        # Column inversion
        self.write_command(0xB4)
        self.write_data(0x07)
        
        # Power control
        self.write_command(0xC0)
        self.write_data(0xA2)
        self.write_data(0x02)
        self.write_data(0x84)
        
        self.write_command(0xC1)
        self.write_data(0xC5)
        
        self.write_command(0xC2)
        self.write_data(0x0A)
        self.write_data(0x00)
        
        self.write_command(0xC3)
        self.write_data(0x8A)
        self.write_data(0x2A)
        
        self.write_command(0xC4)
        self.write_data(0x8A)
        self.write_data(0xEE)
        
        # VCOM control
        self.write_command(0xC5)
        self.write_data(0x0E)
        
        # Memory access control
        self.write_command(0x36)
        self.write_data(0xC8)  # RGB order, row/col flip
        
        # Pixel format
        self.write_command(0x3A)
        self.write_data(0x05)  # 16-bit color
        
        # Gamma settings
        self.write_command(0xE0)
        self.write_data(0x0F)
        self.write_data(0x1A)
        self.write_data(0x0F)
        self.write_data(0x18)
        self.write_data(0x2F)
        self.write_data(0x28)
        self.write_data(0x20)
        self.write_data(0x22)
        self.write_data(0x1F)
        self.write_data(0x1B)
        self.write_data(0x23)
        self.write_data(0x37)
        self.write_data(0x00)
        self.write_data(0x07)
        self.write_data(0x02)
        self.write_data(0x10)
        
        self.write_command(0xE1)
        self.write_data(0x0F)
        self.write_data(0x1B)
        self.write_data(0x0F)
        self.write_data(0x17)
        self.write_data(0x33)
        self.write_data(0x2C)
        self.write_data(0x29)
        self.write_data(0x2E)
        self.write_data(0x30)
        self.write_data(0x30)
        self.write_data(0x39)
        self.write_data(0x3F)
        self.write_data(0x00)
        self.write_data(0x07)
        self.write_data(0x03)
        self.write_data(0x10)
        
        # Display on
        self.write_command(0x29)
        config.delay_ms(100)
        
        # Clear screen
        self.clear()
        
        print("LCD initialization complete!")
        
    def set_window(self, x_start, y_start, x_end, y_end):
        """Set display window"""
        # Column address
        self.write_command(0x2A)
        self.write_data(0x00)
        self.write_data(x_start)
        self.write_data(0x00)
        self.write_data(x_end - 1)
        
        # Row address  
        self.write_command(0x2B)
        self.write_data(0x00)
        self.write_data(y_start)
        self.write_data(0x00)
        self.write_data(y_end - 1)
        
        # Write to RAM
        self.write_command(0x2C)
        
    def clear(self, color=0x0000):
        """Clear screen with specified color"""
        print("Clearing LCD...")
        self.set_window(0, 0, self.width, self.height)
        
        # Create color data
        color_high = (color >> 8) & 0xFF
        color_low = color & 0xFF
        color_data = [color_high, color_low] * (self.width * self.height)
        
        # Send data in chunks for better performance
        chunk_size = 1024
        for i in range(0, len(color_data), chunk_size):
            chunk = color_data[i:i + chunk_size]
            self.write_data_bytes(chunk)
            
    def show_image(self, image):
        """Display PIL Image on LCD"""
        if image is None:
            print("Error: Image is None")
            return
            
        print(f"Displaying image: {image.size}, mode: {image.mode}")
        
        # Resize image to fit display
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
            
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Set display window
        self.set_window(0, 0, self.width, self.height)
        
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Convert RGB888 to RGB565 and create byte array
        color_data = []
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = img_array[y, x]
                # Convert to RGB565
                color565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                color_data.append((color565 >> 8) & 0xFF)  # High byte
                color_data.append(color565 & 0xFF)         # Low byte
        
        # Send data in chunks
        chunk_size = 1024
        for i in range(0, len(color_data), chunk_size):
            chunk = color_data[i:i + chunk_size]
            self.write_data_bytes(chunk)
            
        print("Image displayed successfully!")
        
    def backlight(self, on=True):
        """Control backlight"""
        config.digital_write(config.BL_PIN, 1 if on else 0)
        print(f"Backlight {'ON' if on else 'OFF'}")
        
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up LCD resources...")
        self.backlight(False)
        config.cleanup()