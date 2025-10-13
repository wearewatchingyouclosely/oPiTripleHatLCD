# LCD HAT Library for Orange Pi Zero 2W / Raspberry Pi
# Compatible with both platforms

__version__ = "1.1.0"
__author__ = "Waveshare Team / Orange Pi Community"

# Import main modules
from . import lcdconfig
from . import LCD_0inch96
from . import LCD_1inch3  
from . import Gain_Param

# Platform detection
import os
import sys

def detect_platform():
    """Detect if running on Orange Pi, Raspberry Pi, or other ARM board"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            
        if 'Allwinner' in cpuinfo or 'sun50i' in cpuinfo or 'sun8i' in cpuinfo:
            return "orangepi"
        elif 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo:
            return "raspberrypi"
        else:
            return "unknown"
    except:
        return "unknown"

# Store platform info
PLATFORM = detect_platform()

def get_platform_info():
    """Get information about the current platform"""
    return {
        'platform': PLATFORM,
        'gpio_available': _check_gpio_libraries(),
        'spi_devices': _get_spi_devices()
    }

def _check_gpio_libraries():
    """Check which GPIO libraries are available"""
    available = []
    
    try:
        import OPi.GPIO
        available.append('OPi.GPIO')
    except ImportError:
        pass
        
    try:
        import RPi.GPIO
        available.append('RPi.GPIO')
    except ImportError:
        pass
        
    try:
        import gpiozero
        available.append('gpiozero')
    except ImportError:
        pass
        
    return available

def _get_spi_devices():
    """Get list of available SPI devices"""
    spi_devices = []
    for i in range(3):  # Check SPI0, SPI1, SPI2
        for j in range(3):  # Check CE0, CE1, CE2
            device_path = f'/dev/spidev{i}.{j}'
            if os.path.exists(device_path):
                spi_devices.append(f'spi{i}.{j}')
    return spi_devices

# Print platform info when module is imported (for debugging)
if __name__ == "__main__" or os.environ.get('LCD_HAT_DEBUG'):
    info = get_platform_info()
    print(f"LCD HAT Library v{__version__}")
    print(f"Platform: {info['platform']}")
    print(f"GPIO libraries: {', '.join(info['gpio_available']) if info['gpio_available'] else 'None'}")
    print(f"SPI devices: {', '.join(info['spi_devices']) if info['spi_devices'] else 'None'}")