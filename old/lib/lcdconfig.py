# /*****************************************************************************
# * | File        :	  lcdconfig.py
# * | Author      :   Waveshare team (modified for Orange Pi)
# * | Function    :   Hardware underlying interface
# * | Info        :   Adapted for Orange Pi Zero 2W using sysfs GPIO
# *----------------
# * | This version:   V2.0 (Orange Pi)
# * | Date        :   2025-10-13
# * | Info        :   Uses direct sysfs GPIO access for maximum compatibility
# ******************************************************************************

import os
import sys
import time
import spidev
import logging
import numpy as np

class GPIOPin:
    """Simple GPIO pin wrapper using sysfs"""
    def __init__(self, pin):
        self.pin = pin
        self.value_path = f"/sys/class/gpio/gpio{pin}/value"
        
    def on(self):
        """Set pin HIGH"""
        try:
            with open(self.value_path, 'w') as f:
                f.write('1')
        except:
            pass
            
    def off(self):
        """Set pin LOW"""
        try:
            with open(self.value_path, 'w') as f:
                f.write('0')
        except:
            pass
    
    def close(self):
        """Cleanup pin"""
        pass

class OrangePi:
    """Orange Pi hardware interface using sysfs GPIO"""
    
    def __init__(self, spi=spidev.SpiDev(1,0), spi_freq=10000000, rst=24, dc=4, bl=13, bl_freq=1000, i2c=None, i2c_freq=100000):     
        self.np = np
        self.INPUT = False
        self.OUTPUT = True
        
        self.SPEED = spi_freq
        self.BL_freq = bl_freq
        
        # Store pin numbers
        self.rst_pin = rst
        self.dc_pin = dc
        self.bl_pin = bl
        
        # Initialize GPIO pins via sysfs
        self._export_gpio(rst)
        self._export_gpio(dc)
        self._export_gpio(bl)
        
        time.sleep(0.1)  # Wait for export
        
        self._set_direction(rst, "out")
        self._set_direction(dc, "out")
        self._set_direction(bl, "out")
        
        # Create pin objects
        self.RST_PIN = GPIOPin(rst)
        self.DC_PIN = GPIOPin(dc)
        self.BL_PIN = GPIOPin(bl)
        
        # Backlight control (simple on/off for now, no PWM)
        self.bl_state = 1.0
        
        # Initialize SPI
        self.SPI = spi
        if self.SPI != None:
            self.SPI.max_speed_hz = spi_freq
            self.SPI.mode = 0b00
    
    def _export_gpio(self, pin):
        """Export GPIO pin via sysfs"""
        try:
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(pin))
        except:
            # Pin might already be exported
            pass
    
    def _unexport_gpio(self, pin):
        """Unexport GPIO pin"""
        try:
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write(str(pin))
        except:
            pass
    
    def _set_direction(self, pin, direction):
        """Set GPIO direction (in/out)"""
        try:
            with open(f'/sys/class/gpio/gpio{pin}/direction', 'w') as f:
                f.write(direction)
        except Exception as e:
            logging.warning(f"Could not set direction for GPIO {pin}: {e}")

    def gpio_mode(self, Pin, Mode, pull_up=None, active_state=True):
        """Configure GPIO pin - returns the pin object"""
        return GPIOPin(Pin)

    def digital_write(self, pin, value):
        """Write digital value to pin"""
        if value:
            pin.on()
        else:
            pin.off()

    def digital_read(self, pin):
        """Read digital value from pin"""
        try:
            with open(pin.value_path, 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def delay_ms(self, delaytime):
        """Delay in milliseconds"""
        time.sleep(delaytime / 1000.0)

    def gpio_pwm(self, Pin):
        """Setup PWM on pin - simplified, returns regular pin"""
        return GPIOPin(Pin)
        
    def spi_writebyte(self, data):
        """Write data to SPI"""
        if self.SPI != None:
            self.SPI.writebytes(data)
            
    def bl_DutyCycle(self, duty):
        """Set backlight duty cycle (0-100) - simplified to on/off"""
        self.bl_state = duty / 100.0
        if duty > 0:
            self.BL_PIN.on()
        else:
            self.BL_PIN.off()
        
    def bl_Frequency(self, freq):
        """Set backlight PWM frequency - not implemented in simple mode"""
        pass
           
    def module_init(self):
        """Initialize the module"""
        if self.SPI != None:
            self.SPI.max_speed_hz = self.SPEED        
            self.SPI.mode = 0b00     
        return 0

    def module_exit(self):
        """Cleanup on exit"""
        logging.debug("spi end")
        if self.SPI != None:
            self.SPI.close()
        
        logging.debug("gpio cleanup...")
        self.digital_write(self.RST_PIN, 1)
        self.digital_write(self.DC_PIN, 0)
        self.BL_PIN.off()
        
        # Unexport GPIOs
        self._unexport_gpio(self.rst_pin)
        self._unexport_gpio(self.dc_pin)
        self._unexport_gpio(self.bl_pin)
        
        time.sleep(0.001)

### END OF FILE ###
