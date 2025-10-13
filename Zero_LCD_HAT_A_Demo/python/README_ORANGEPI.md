# oPiTripleHatLCD

Orange Pi Zero 2W support for Waveshare Zero LCD HAT (A)

This repository provides updated drivers and examples for using the **Waveshare Zero LCD HAT (A)** with Orange Pi Zero 2W running Armbian. The original code was designed for Raspberry Pi and has been modified to work with Orange Pi hardware and GPIO libraries.

**Hardware Product**: [Waveshare Zero LCD HAT (A)](https://www.waveshare.com/zero-lcd-hat-a.htm)

## Hardware Requirements

- Orange Pi Zero 2W (H618 SoC)
- Waveshare Zero LCD HAT (A) - Available at: https://www.waveshare.com/zero-lcd-hat-a.htm
- MicroSD card with Armbian OS (Bookworm/Jammy recommended)
- Stable power supply (5V/2A minimum)

## Prerequisites

- Orange Pi Zero 2W with Armbian installed and configured
- SSH access to your Orange Pi (setting up SSH is out of scope for this guide)
- Basic familiarity with Linux command line
- SPI interface enabled on your Orange Pi

## GPIO Pin Mapping for Orange Pi Zero 2W

The Orange Pi Zero 2W uses different GPIO numbering than Raspberry Pi. Here are the updated pin assignments:

### Single Display Configuration:
- **RST (Reset)**: GPIO 11 (Physical pin 26)
- **DC (Data/Command)**: GPIO 12 (Physical pin 32)
- **BL (Backlight)**: GPIO 13 (Physical pin 33)
- **SPI Bus**: 1 (SPI1)
- **SPI Device**: 0 (CE0)

### Dual Display Configuration:
- **Display 0**: RST=11, DC=12, BL=13, SPI1.0
- **Display 1**: RST=15, DC=16, BL=18, SPI1.1

## Quick Start

### 1. Clone the Repository

```bash
# SSH into your Orange Pi Zero 2W (SSH setup is out of scope for this guide)
# Clone the repository
git clone https://github.com/yourusername/oPiTripleHatLCD.git
cd oPiTripleHatLCD/python
```

### 2. Enable SPI on Orange Pi Zero 2W
```bash
# Method 1: Use your distro's hardware config tool (recommended)
# Armbian:
sudo armbian-config
# Orange Pi images:
sudo orangepi-config
# Raspberry Pi:
sudo raspi-config

# In the menu: find "System" / "Hardware" / "SPI" (or similar) and enable spi/spidev, then reboot

# --- OR ---

# Method 2: Load modules immediately and persistently
# (Replace the SoC driver name if needed: spi-sun50i-h616, spi-sunxi, spi-bcm2708, etc.)
sudo modprobe spi-sun50i-h616
sudo modprobe spidev

# Make persistent across reboots:
echo 'spi-sun50i-h616' | sudo tee -a /etc/modules
echo 'spidev' | sudo tee -a /etc/modules

# --- OR ---

# Method 3: Enable via device-tree overlay (common on Armbian)
# Edit /boot/armbianEnv.txt and add (or append) the overlay:
sudo nano /boot/armbianEnv.txt
# Add or update a line:
# overlays=spi-spidev
# Save and reboot

# Verify SPI is available
ls -la /dev/spi*
lsmod | grep spi
dmesg | grep -i spi

# Optional: allow non-root access to SPI/GPIO
sudo usermod -a -G spi,gpio $USER
# Then log out and log back in
```

### 3. Run the Automated Installation

```bash
# Run the automated installation script
sudo bash install_orangepi.sh

# Or install manually:
sudo apt update
sudo apt install -y python3-pip python3-dev python3-pil python3-numpy python3-spidev
sudo pip3 install OPi.GPIO psutil
```

### 4. Test Your Setup

```bash
# Run the test script to verify everything is working
sudo python3 test_orangepi.py
```

### 5. Verify SPI is Working

```bash
# Check for SPI devices
ls -la /dev/spi*
# You should see: /dev/spidev1.0 (and /dev/spidev1.1 for dual displays)

# Check SPI module is loaded
lsmod | grep spi
```

## Running the Demos

### Basic Display Test
```bash
cd example
sudo python3 orangepi_demo.py
```

### CPU Monitoring (Single or Dual Display)
```bash
sudo python3 orangepi_cpu.py
```

### Original Examples (Updated)
```bash
# These work with modifications for Orange Pi GPIO
sudo python3 0inch96_spi0ce0.py  # Use SPI1 instead
sudo python3 CPU.py              # Updated for Orange Pi
```

## Troubleshooting

### SPI Not Working
1. **Check SPI is enabled**:
   ```bash
   ls /dev/spi*
   ```

2. **Enable SPI manually**:
   ```bash
   sudo orangepi-config
   # Go to System -> Hardware -> spi-spidev
   ```

3. **Check kernel modules**:
   ```bash
   lsmod | grep spi
   sudo modprobe spi-sun50i-h616
   sudo modprobe spidev
   ```

### GPIO Library Issues
1. **Install OPi.GPIO** (preferred for Orange Pi):
   ```bash
   sudo pip3 install OPi.GPIO
   ```

2. **Alternative GPIO libraries**:
   ```bash
   sudo pip3 install RPi.GPIO  # May work on some Armbian images
   sudo apt install python3-gpiozero  # Fallback option
   ```

### Display Not Working
1. **Check connections**: Ensure the HAT is properly connected
2. **Verify pin assignments**: Use a multimeter to check continuity
3. **Test with different SPI speeds**: Try lower frequencies (1MHz instead of 10MHz)
4. **Check permissions**: Make sure you're running with `sudo`

### Permission Issues
```bash
# Add user to required groups
sudo usermod -a -G spi,gpio $USER
# Then logout and login again
```

## Key Differences from Raspberry Pi

1. **GPIO Library**: Uses `OPi.GPIO` instead of `RPi.GPIO`
2. **SPI Bus**: Typically uses SPI1 instead of SPI0
3. **GPIO Numbering**: Different pin assignments
4. **Thermal Zones**: Different paths for temperature monitoring
5. **Hardware Detection**: Uses Allwinner SoC detection

## File Structure

```
python/
├── lib/
│   ├── lcdconfig.py          # Updated with Orange Pi support
│   ├── LCD_0inch96.py        # LCD driver (unchanged)
│   ├── LCD_1inch3.py         # LCD driver (unchanged)
│   └── Gain_Param.py         # Updated temperature monitoring
├── example/
│   ├── orangepi_demo.py      # New Orange Pi demo
│   ├── orangepi_cpu.py       # New CPU monitor for Orange Pi
│   └── [original examples]   # May need pin updates
├── install_orangepi.sh       # Automated installation script
└── README_ORANGEPI.md        # This file
```

## Hardware Compatibility

This code has been tested with:
- Orange Pi Zero 2W (H618 SoC)
- Armbian 24.x (Bookworm/Jammy based)
- Waveshare 0.96" LCD HAT

Should also work with:
- Other Orange Pi models with SPI support
- Other Allwinner H6/H618 based boards
- Other ARM boards running Armbian

## Notes

- Always run Python scripts with `sudo` for GPIO access
- The original Raspberry Pi examples may need GPIO pin updates
- SPI1 is preferred over SPI0 to avoid conflicts
- Dual display support requires SPI1.1 to be available
- Some Orange Pi models may have different GPIO pin layouts

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your hardware connections
3. Ensure SPI is properly enabled in Armbian
4. Check that all required Python packages are installed
5. Try the basic demo first before advanced features