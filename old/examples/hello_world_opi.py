#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hello World Example for Waveshare Zero LCD HAT (A) on Orange Pi Zero 2W
Using OPi.GPIO library for proper GPIO control

This example demonstrates:
- Proper OPi.GPIO library usage with BOARD pin numbering
- LCD initialization and display
- Text rendering and image display
- GPIO cleanup

Hardware Requirements:
- Orange Pi Zero 2W with Armbian
- Waveshare Zero LCD HAT (A) with 0.96" LCD
- SPI enabled (use armbian-config -> System -> Kernel -> DTO001)

Software Requirements:
- OPi.GPIO library
- PIL (Pillow) 
- numpy
- spidev
"""

import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont
import traceback

# Add lib directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))

try:
    from LCD_0inch96_opi import LCD_0inch96
    import lcdconfig_opi as config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this on Orange Pi with required libraries installed")
    sys.exit(1)

def create_hello_world_image(width=160, height=80):
    """Create a Hello World image with system info"""
    # Create image with black background
    image = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    try:
        # Try to load a font (fallback to default if not available)
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        # Use default font if truetype not available
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Get current time
    current_time = time.strftime("%H:%M:%S")
    
    # Draw text
    draw.text((10, 5), "Hello World!", fill=(255, 255, 255), font=font_large)
    draw.text((10, 25), "Orange Pi Zero 2W", fill=(0, 255, 0), font=font_small)
    draw.text((10, 40), "LCD HAT Test", fill=(0, 255, 255), font=font_small)
    draw.text((10, 55), f"Time: {current_time}", fill=(255, 255, 0), font=font_small)
    
    # Draw a simple border
    draw.rectangle([0, 0, width-1, height-1], outline=(255, 0, 0), width=1)
    
    return image

def create_test_pattern(width=160, height=80):
    """Create a colorful test pattern"""
    image = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Create gradient bars
    for x in range(width):
        for y in range(height // 3):
            # Red gradient
            color = (int(255 * x / width), 0, 0)
            draw.point((x, y), fill=color)
            
            # Green gradient  
            color = (0, int(255 * x / width), 0)
            draw.point((x, y + height // 3), fill=color)
            
            # Blue gradient
            color = (0, 0, int(255 * x / width))
            draw.point((x, y + 2 * height // 3), fill=color)
    
    return image

def main():
    """Main demo function"""
    print("=" * 50)
    print("Orange Pi Zero 2W LCD HAT Test")
    print("Using OPi.GPIO library")
    print("=" * 50)
    
    lcd = None
    
    try:
        # Initialize LCD
        print("\n1. Initializing LCD...")
        lcd = LCD_0inch96()
        lcd.init_lcd()
        
        # Turn on backlight
        print("\n2. Turning on backlight...")
        lcd.backlight(True)
        time.sleep(1)
        
        # Test 1: Hello World
        print("\n3. Displaying Hello World...")
        hello_image = create_hello_world_image()
        lcd.show_image(hello_image)
        time.sleep(3)
        
        # Test 2: Color test pattern
        print("\n4. Displaying color test pattern...")
        test_image = create_test_pattern()
        lcd.show_image(test_image)
        time.sleep(3)
        
        # Test 3: Backlight toggle
        print("\n5. Testing backlight control...")
        for i in range(3):
            print(f"   Backlight OFF ({i+1}/3)")
            lcd.backlight(False)
            time.sleep(0.5)
            print(f"   Backlight ON ({i+1}/3)")
            lcd.backlight(True)
            time.sleep(0.5)
        
        # Test 4: Final message
        print("\n6. Displaying completion message...")
        final_image = Image.new('RGB', (160, 80), (0, 0, 0))
        draw = ImageDraw.Draw(final_image)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 20), "TEST COMPLETE!", fill=(0, 255, 0), font=font)
        draw.text((10, 40), "HAT Working!", fill=(255, 255, 255), font=font)
        lcd.show_image(final_image)
        
        print("\n" + "=" * 50)
        print("SUCCESS! LCD HAT is working correctly!")
        print("Key information:")
        print(f"- LCD Resolution: {lcd.width}x{lcd.height}")
        print(f"- GPIO Library: OPi.GPIO (BOARD pin numbering)")
        print(f"- SPI Bus: {config.SPI_BUS}, Device: {config.SPI_DEVICE}")
        print(f"- Pin assignments:")
        print(f"  RST = Pin {config.RST_PIN} (Physical)")
        print(f"  DC  = Pin {config.DC_PIN} (Physical)") 
        print(f"  CS  = Pin {config.CS_PIN} (Physical)")
        print(f"  BL  = Pin {config.BL_PIN} (Physical)")
        print("=" * 50)
        
        # Keep display on for a while
        print("\nTest complete! Display will stay on for 10 seconds...")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("Full traceback:")
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Check SPI is enabled: armbian-config -> System -> Kernel -> DTO001")
        print("2. Check HAT is properly seated on GPIO header")
        print("3. Verify this is running on Orange Pi Zero 2W")
        print("4. Check all required libraries are installed")
    finally:
        # Clean up
        if lcd:
            print("\nCleaning up...")
            lcd.cleanup()
        print("Done!")

if __name__ == "__main__":
    main()