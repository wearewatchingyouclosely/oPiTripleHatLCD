# Orange Pi Zero 2W + Waveshare Zero LCD HAT (A) - Hello World

This project provides a complete "Hello World" example for testing the **Waveshare Zero LCD HAT (A)** on the **Orange Pi Zero 2W** using the proper **OPi.GPIO** library.

## ✅ What's Working

- **OPi.GPIO Library**: Drop-in replacement for RPi.GPIO with proper Orange Pi support
- **BOARD Pin Numbering**: Uses physical pin numbers (not GPIO chip numbers)  
- **SPI Communication**: Bus 1, Device 0 (/dev/spidev1.0)
- **LCD Display**: 0.96" 160x80 pixel ST7735S controller
- **GPIO Control**: Reset, Data/Command, Chip Select, Backlight pins
- **Hardware Compatibility**: RPi HAT physical layout works on Orange Pi Zero 2W

## 🔧 Hardware Setup

### Requirements
- **Orange Pi Zero 2W** (H618 SoC)
- **Waveshare Zero LCD HAT (A)** with 0.96" display
- **Armbian OS** (or compatible Linux distribution)

### Physical Connection
The HAT connects directly to the Orange Pi GPIO header. Despite different GPIO numbering, the **physical pin layout is compatible** between Raspberry Pi and Orange Pi Zero 2W.

## 🛠️ Software Installation

### 1. Enable SPI
```bash
# Run armbian-config
sudo armbian-config

# Navigate to: System → Kernel → DTO001 (Enable SPI)
# Reboot when prompted
sudo reboot
```

### 2. Install Required Libraries
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python development tools
sudo apt install -y python3-dev python3-pip python3-setuptools

# Install system libraries
sudo apt install -y libfreetype6-dev libjpeg-dev libopenjp2-7 libtiff5

# Install Python packages
pip3 install --user OPi.GPIO
pip3 install --user spidev
pip3 install --user Pillow
pip3 install --user numpy
```

### 3. Download Project Files
```bash
# Create project directory
mkdir -p ~/lcd_hat_test
cd ~/lcd_hat_test

# Create lib directory
mkdir -p lib

# Create examples directory  
mkdir -p examples
```

**Copy these files to your Orange Pi:**

**lib/lcdconfig_opi.py** - OPi.GPIO configuration
**lib/LCD_0inch96_opi.py** - LCD driver using OPi.GPIO
**examples/hello_world_opi.py** - Hello World demo

## 🚀 Running the Test

```bash
cd ~/lcd_hat_test
python3 examples/hello_world_opi.py
```

### Expected Output
```
==================================================
Orange Pi Zero 2W LCD HAT Test
Using OPi.GPIO library
==================================================

1. Initializing LCD...
Initializing OPi.GPIO...
GPIO pins configured:
  RST_PIN = 22 (Physical)
  DC_PIN = 18 (Physical)
  CS_PIN = 24 (Physical)
  BL_PIN = 12 (Physical)
SPI initialized: bus=1, device=0
Performing LCD reset...
Sending LCD initialization commands...
LCD initialization complete!

2. Turning on backlight...
Backlight ON

3. Displaying Hello World...
Image displayed successfully!

4. Displaying color test pattern...
Image displayed successfully!

5. Testing backlight control...
   Backlight OFF (1/3)
   Backlight ON (1/3)
   [... continues ...]

6. Displaying completion message...
Image displayed successfully!

==================================================
SUCCESS! LCD HAT is working correctly!
Key information:
- LCD Resolution: 160x80
- GPIO Library: OPi.GPIO (BOARD pin numbering)
- SPI Bus: 1, Device: 0
- Pin assignments:
  RST = Pin 22 (Physical)
  DC  = Pin 18 (Physical)
  CS  = Pin 24 (Physical)
  BL  = Pin 12 (Physical)
==================================================
```

## 📌 Pin Mapping Details

### Physical Pin Layout
The Orange Pi Zero 2W uses the **same physical pin layout** as Raspberry Pi:

| Function | Physical Pin | Orange Pi GPIO | RPi BCM | HAT Connection |
|----------|-------------|----------------|---------|----------------|
| RST      | 22          | PC8 (GPIO72)   | GPIO25  | Reset          |
| DC       | 18          | PC7 (GPIO71)   | GPIO24  | Data/Command   |
| CS       | 24          | PC10 (GPIO74)  | GPIO8   | Chip Select    |
| BL       | 12          | PC1 (GPIO65)   | GPIO18  | Backlight      |
| MOSI     | 19          | PC2 (GPIO66)   | GPIO10  | SPI Data       |
| SCLK     | 23          | PC0 (GPIO64)   | GPIO11  | SPI Clock      |

### Key Insight: BOARD vs GPIO Numbers
- **OPi.GPIO uses BOARD numbering** (physical pin numbers: 12, 18, 22, 24)
- **NOT the GPIO chip numbers** (65, 71, 72, 74) we discovered earlier
- This makes the code much simpler and compatible with RPi examples!

## 🔍 How OPi.GPIO Works

The **OPi.GPIO** library is a **drop-in replacement** for RPi.GPIO that:

1. **Translates pin numbers**: BOARD pins → Orange Pi GPIO chips internally
2. **Uses same API**: `GPIO.setup()`, `GPIO.output()`, `GPIO.input()`
3. **Handles sysfs**: Manages `/sys/class/gpio` operations automatically
4. **Supports multiple boards**: Orange Pi Zero, Plus, PC, etc.

### Code Comparison

**Old Approach (Custom sysfs)**:
```python
# Manual GPIO chip number management
pin_73 = 73  # PC9
echo_command = f"echo {pin_73} > /sys/class/gpio/export"
```

**New Approach (OPi.GPIO)**:
```python
# Standard GPIO library calls
import OPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(22, GPIO.OUT)  # Physical pin 22
GPIO.output(22, GPIO.HIGH)
```

## 🐛 Troubleshooting

### SPI Not Working
```bash
# Check SPI is enabled
ls -la /dev/spi*
# Should show: /dev/spidev1.0

# If missing, enable in armbian-config
sudo armbian-config
# System → Kernel → DTO001
```

### GPIO Permission Errors
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
# Log out and back in

# Or run with sudo (not recommended)
sudo python3 examples/hello_world_opi.py
```

### Import Errors
```bash
# Check OPi.GPIO installation
python3 -c "import OPi.GPIO; print('OPi.GPIO OK')"

# Reinstall if needed
pip3 install --user --force-reinstall OPi.GPIO
```

### Display Not Working
1. **Check HAT seating**: Ensure HAT is properly connected to all 40 pins
2. **Verify SPI**: `ls /dev/spidev1.0` should exist
3. **Test GPIO**: Run the hello world script and check for GPIO initialization messages
4. **Check power**: HAT LED should be lit when powered

## 📚 Code Structure

### lib/lcdconfig_opi.py
- OPi.GPIO initialization and configuration
- Pin definitions using BOARD numbering
- SPI setup and GPIO helper functions
- Resource cleanup

### lib/LCD_0inch96_opi.py
- LCD driver for ST7735S controller
- Image display and text rendering
- Hardware initialization sequences
- Backlight control

### examples/hello_world_opi.py
- Complete test demonstration
- Multiple display tests
- Error handling and diagnostics
- Hardware verification

## 🎯 Success Criteria

When working correctly, you should see:
1. ✅ SPI device `/dev/spidev1.0` exists
2. ✅ GPIO pins initialize without errors  
3. ✅ LCD backlight turns on/off
4. ✅ "Hello World" text displays clearly
5. ✅ Color test pattern shows RGB gradients
6. ✅ No error messages in console output

## 🔄 Next Steps

With the HAT working, you can:
- Display sensor data (temperature, CPU usage, etc.)
- Create status dashboards  
- Show network information
- Build custom graphics and animations
- Interface with other Orange Pi peripherals

## 📞 Support

If you encounter issues:
1. **Check hardware**: HAT seating, SPI enabled, power connections
2. **Verify software**: All libraries installed, correct Python version
3. **Review output**: Error messages provide specific troubleshooting steps
4. **Test systematically**: Run each component individually

The OPi.GPIO approach provides much better compatibility and maintainability compared to direct sysfs GPIO manipulation!