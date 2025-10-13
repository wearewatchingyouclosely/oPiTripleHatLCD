# /*****************************************************************************
# * | File        :	  lcdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-06-21
# * | Info        :   
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import sys
import time
import spidev
import logging
import numpy as np

try:
    # Try OrangePi.GPIO first (preferred for Orange Pi)
    import OPi.GPIO as GPIO
    GPIO_AVAILABLE = "OPI"
except ImportError:
    try:
        # Fallback to RPi.GPIO if available (some Armbian images include it)
        import RPi.GPIO as GPIO
        GPIO_AVAILABLE = "RPI"
    except ImportError:
        try:
            # Last resort: use gpiozero if available
            from gpiozero import *
            GPIO_AVAILABLE = "GPIOZERO"
        except ImportError:
            raise ImportError("No GPIO library found. Please install OPi.GPIO or RPi.GPIO")

class RaspberryPi:
    def __init__(self,spi=spidev.SpiDev(0,0),spi_freq=40000000,rst = 22,dc = 23,bl = 19,bl_freq=1000,i2c=None,i2c_freq=100000):     
        self.np=np
        self.INPUT = False
        self.OUTPUT = True
        
        self.SPEED  =spi_freq
        self.BL_freq=bl_freq
        
        # Store pin numbers for GPIO library usage
        self.rst_pin = rst
        self.dc_pin = dc
        self.bl_pin = bl
        
        # Initialize GPIO based on available library
        if GPIO_AVAILABLE in ["OPI", "RPI"]:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
        #Initialize GPIO
        self.RST_PIN= self.gpio_mode(rst,self.OUTPUT)
        self.DC_PIN = self.gpio_mode(dc,self.OUTPUT)
        self.BL_PIN = self.gpio_pwm(bl)

        #Initialize SPI
        self.SPI = spi
        if self.SPI!=None :
            self.SPI.max_speed_hz = spi_freq
            self.SPI.mode = 0b00

    def gpio_mode(self,Pin,Mode,pull_up = None,active_state = True):
        if GPIO_AVAILABLE in ["OPI", "RPI"]:
            if Mode:  # OUTPUT
                GPIO.setup(Pin, GPIO.OUT)
                return Pin
            else:  # INPUT
                if pull_up is None:
                    GPIO.setup(Pin, GPIO.IN)
                elif pull_up:
                    GPIO.setup(Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                else:
                    GPIO.setup(Pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                return Pin
        elif GPIO_AVAILABLE == "GPIOZERO":
            if Mode:
                return DigitalOutputDevice(Pin,active_high = True,initial_value =False)
            else:
                return DigitalInputDevice(Pin,pull_up=pull_up,active_state=active_state)

    def digital_write(self, pin, value):
        if GPIO_AVAILABLE in ["OPI", "RPI"]:
            if isinstance(pin, int):
                GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)
        elif GPIO_AVAILABLE == "GPIOZERO":
            if value:
                pin.on()
            else:
                pin.off()

    def digital_read(self, pin):
        if GPIO_AVAILABLE in ["OPI", "RPI"]:
            if isinstance(pin, int):
                return GPIO.input(pin) == GPIO.HIGH
        elif GPIO_AVAILABLE == "GPIOZERO":
            return pin.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def gpio_pwm(self,Pin):
        if GPIO_AVAILABLE in ["OPI", "RPI"]:
            GPIO.setup(Pin, GPIO.OUT)
            pwm = GPIO.PWM(Pin, self.BL_freq)
            pwm.start(0)
            return pwm
        elif GPIO_AVAILABLE == "GPIOZERO":
            return PWMOutputDevice(Pin,frequency = self.BL_freq)
        
    def spi_writebyte(self, data):
        if self.SPI!=None :
            self.SPI.writebytes(data)
    def bl_DutyCycle(self, duty):
        if GPIO_AVAILABLE in ["OPI", "RPI"]:
            if hasattr(self.BL_PIN, 'ChangeDutyCycle'):
                self.BL_PIN.ChangeDutyCycle(duty)
        elif GPIO_AVAILABLE == "GPIOZERO":
            self.BL_PIN.value = duty / 100
        
    def bl_Frequency(self,freq):
        if GPIO_AVAILABLE in ["OPI", "RPI"]:
            if hasattr(self.BL_PIN, 'ChangeFrequency'):
                self.BL_PIN.ChangeFrequency(freq)
        elif GPIO_AVAILABLE == "GPIOZERO":
            self.BL_PIN.frequency = freq
           
    def module_init(self):
        if self.SPI!=None :
            self.SPI.max_speed_hz = self.SPEED        
            self.SPI.mode = 0b00     
        return 0

    def module_exit(self):
        logging.debug("spi end")
        if self.SPI!=None :
            self.SPI.close()
        
        logging.debug("gpio cleanup...")
        self.digital_write(self.RST_PIN, 1)
        self.digital_write(self.DC_PIN, 0)   
        
        if GPIO_AVAILABLE in ["OPI", "RPI"]:
            if hasattr(self.BL_PIN, 'stop'):
                self.BL_PIN.stop()
            GPIO.cleanup()
        elif GPIO_AVAILABLE == "GPIOZERO":
            self.BL_PIN.close()
        
        time.sleep(0.001)


# Platform detection and initialization
def get_platform_implementation():
    """Detect the platform and return appropriate GPIO implementation"""
    # Check if we're on Orange Pi or other ARM board with Allwinner SoC
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Allwinner' in cpuinfo or 'sun50i' in cpuinfo or 'sun8i' in cpuinfo:
                return RaspberryPi()  # Use the same class but with Orange Pi GPIO
    except:
        pass
    
    # Check for Raspberry Pi
    if os.path.exists('/sys/bus/platform/drivers/gpiomem-bcm2835'):
        return RaspberryPi()
    
    # Default to our implementation (should work on most ARM boards with Armbian)
    return RaspberryPi()

# Don't auto-initialize - let the user create the implementation manually
# This prevents issues when importing the module without hardware present

### END OF FILE ###
