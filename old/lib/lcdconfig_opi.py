# -*- coding: utf-8 -*-
"""
OPi.GPIO-based configuration for Orange Pi Zero 2W
Pin mappings for Waveshare Zero LCD HAT (A) using BOARD pin numbering
"""

import OPi.GPIO as GPIO
import time
import spidev

# Pin definitions using BOARD numbering (physical pin numbers)
# These correspond to the GPIO header pins on Orange Pi Zero 2W
RST_PIN = 22  # Physical pin 22 (PC8/GPIO72)
DC_PIN = 18   # Physical pin 18 (PC7/GPIO71) 
CS_PIN = 24   # Physical pin 24 (PC10/GPIO74)
BL_PIN = 12   # Physical pin 12 (PC1/GPIO65)

# SPI configuration
SPI_BUS = 1
SPI_DEVICE = 0

class OrangePiGPIO:
    """Orange Pi GPIO controller using OPi.GPIO library"""
    
    def __init__(self):
        self.initialized = False
        self.spi = None
        
    def digital_write(self, pin, value):
        """Write digital value to pin"""
        if not self.initialized:
            self.setup()
        GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)
        
    def digital_read(self, pin):
        """Read digital value from pin"""
        if not self.initialized:
            self.setup()
        return GPIO.input(pin)
        
    def setup(self):
        """Initialize GPIO system"""
        if self.initialized:
            return
            
        print("Initializing OPi.GPIO...")
        
        # Set pin numbering mode to BOARD (physical pin numbers)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Set up pins as outputs
        GPIO.setup(RST_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(DC_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(CS_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(BL_PIN, GPIO.OUT, initial=GPIO.HIGH)
        
        print(f"GPIO pins configured:")
        print(f"  RST_PIN = {RST_PIN} (Physical)")
        print(f"  DC_PIN = {DC_PIN} (Physical)")
        print(f"  CS_PIN = {CS_PIN} (Physical)")
        print(f"  BL_PIN = {BL_PIN} (Physical)")
        
        # Initialize SPI
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(SPI_BUS, SPI_DEVICE)
            self.spi.max_speed_hz = 4000000
            self.spi.mode = 0
            print(f"SPI initialized: bus={SPI_BUS}, device={SPI_DEVICE}")
        except Exception as e:
            print(f"SPI initialization failed: {e}")
            raise
            
        self.initialized = True
        
    def spi_writebyte(self, data):
        """Write single byte via SPI"""
        if not self.initialized:
            self.setup()
        if isinstance(data, list):
            self.spi.writebytes(data)
        else:
            self.spi.writebytes([data])
            
    def spi_writebytes(self, data):
        """Write multiple bytes via SPI"""
        if not self.initialized:
            self.setup()
        self.spi.writebytes(data)
        
    def delay_ms(self, ms):
        """Delay in milliseconds"""
        time.sleep(ms / 1000.0)
        
    def cleanup(self):
        """Clean up GPIO and SPI resources"""
        if self.spi:
            self.spi.close()
            self.spi = None
        if self.initialized:
            GPIO.cleanup()
            self.initialized = False
            print("OPi.GPIO cleaned up")

# Create global instance
OPiGPIO = OrangePiGPIO()

# Convenience functions for backward compatibility
def digital_write(pin, value):
    OPiGPIO.digital_write(pin, value)

def digital_read(pin):
    return OPiGPIO.digital_read(pin)

def spi_writebyte(data):
    OPiGPIO.spi_writebyte(data)

def spi_writebytes(data):
    OPiGPIO.spi_writebytes(data)

def delay_ms(ms):
    OPiGPIO.delay_ms(ms)

def cleanup():
    OPiGPIO.cleanup()