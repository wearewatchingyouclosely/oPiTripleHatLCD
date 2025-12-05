# Orange Pi Zero 2W - Waveshare Zero LCD HAT (A)

Python drivers and examples for using the **Waveshare Zero LCD HAT (A)** with **Orange Pi Zero 2W** (H618 SoC) running Armbian.

## Hardware

- **Product**: [Waveshare Zero LCD HAT (A)](https://www.waveshare.com/zero-lcd-hat-a.htm)
- **Wiki**: [Zero LCD HAT (A) Documentation](https://www.waveshare.com/wiki/Zero_LCD_HAT_(A))
- **Displays**: Two 0.96" (160x80px) ST7735S LCD screens OR one 1.3" (240x240px) IPS LCD
- **Interface**: SPI
- **Board**: Orange Pi Zero 2W with Armbian

## Requirements

- Orange Pi Zero 2W with Armbian OS installed
- SSH or terminal access
- Waveshare Zero LCD HAT (A) connected
- Power supply (5V/2A minimum recommended)

## Installation

### 1. Install Git (if not already installed)

```bash
sudo apt update
sudo apt install -y git
```

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/yourusername/oPiTripleHatLCD.git
cd oPiTripleHatLCD
```

**Alternative (no git)**: Download ZIP from GitHub, transfer to Orange Pi, and extract:
```bash
unzip oPiTripleHatLCD-main.zip
cd oPiTripleHatLCD-main
```

### 3. Enable SPI on Orange Pi

Use armbian-config to enable SPI:

```bash
sudo armbian-config
```

Navigate to: **System → Kernel → DTO001** and enable **spi-spidev**

**Important**: After enabling, **reboot** your Orange Pi:
```bash
sudo reboot
```

After reboot, verify SPI devices exist:
```bash
ls -la /dev/spi*
# Should show: /dev/spidev1.0 and /dev/spidev1.1
```

### 4. Install Python Dependencies

```bash
sudo apt install -y python3-pip python3-pil python3-numpy python3-spidev python3-gpiozero python3-lgpio
```

**Note**: Orange Pi uses `gpiozero` with `lgpio` backend instead of RPi.GPIO.

If `python3-gpiozero` or `python3-lgpio` are not available in apt, use pip with system packages flag:
```bash
sudo pip3 install --break-system-packages gpiozero lgpio
```

## Quick Start - Hello World

Run the hello world demo to display images on the LCD:

```bash
cd ~/oPiTripleHatLCD/examples
sudo python3 hello_world.py
```

This will:
1. Initialize the 0.96" LCD display
2. Show the first image from `pic/` folder (LCD_0inch96.jpg)
3. Wait 3 seconds
4. Show the second image from `pic/` folder (LCD_1inch3.jpg)
5. Wait 3 seconds and exit

## Pin Configuration

For Orange Pi Zero 2W, using available GPIO pins:

**Display 1 (SPI1.0):**
- RST (Reset): GPIO 71 (PC7)
- DC (Data/Command): GPIO 72 (PC8)
- BL (Backlight): GPIO 73 (PC9)
- SPI Bus: 1 (PH6/7/8/9), Device: 0

**Important**: Orange Pi Zero 2W uses GPIO chip numbers, not BCM or physical pin numbers:
- PC bank starts at GPIO 64 (PC0=64, PC1=65, ... PC9=73)
- PH bank starts at GPIO 224 (PH0=224, PH1=225, etc.)
- SPI1 uses: PH6(MOSI), PH7(MISO), PH8(CLK), PH9(CS0)

To verify available GPIOs:
```bash
# Check which pins are unclaimed/available
sudo cat /sys/kernel/debug/pinctrl/300b000.pinctrl/pinmux-pins | grep UNCLAIMED
```

**Hardware Wiring**: You'll need to wire the HAT to these specific GPIO pins on the Orange Pi 40-pin header.

## Troubleshooting

### No /dev/spi* devices

If SPI devices don't appear after enabling in armbian-config:

**Step 1: Verify overlay is enabled**
```bash
cat /boot/armbianEnv.txt | grep overlays
# Should contain: overlays=spi-spidev
```

**Step 2: Check for kernel errors**
```bash
dmesg | grep -i spi | tail -20
```

If you see errors like `"Error applying setting, reverse things back"`:

This indicates a device tree / pinmux issue common with some H616 Armbian builds. Try these solutions:

**Solution A: Try param overlay (recommended)**
```bash
sudo nano /boot/armbianEnv.txt
```
Add this line after the overlays line:
```
param_spidev_spi_bus=1
param_spidev_spi_cs=0
```
Save, reboot, and check `ls /dev/spi*`

**Solution B: Manual module loading**
```bash
sudo modprobe spi_sun6i
sudo modprobe spidev
ls -la /dev/spi*
```

**Solution C: Try edge kernel**

If using Armbian "current" kernel, switch to "edge":
```bash
sudo armbian-config
# System → Kernel → select an "edge" kernel version
# Reboot after installing
```

**Solution D: Check conflicting overlays**

Remove any conflicting overlays like tft35_spi:
```bash
sudo nano /boot/armbianEnv.txt
# Change: overlays=spi-spidev tft35_spi
# To: overlays=spi-spidev
```

**Known Issue:** Some Orange Pi Zero 2W Armbian images (especially older builds) have incomplete H616 SPI device tree support. If none of the above work, you may need to update to a newer Armbian image (24.8.0+) or use the edge kernel.

### Permission errors

Add your user to SPI group:
```bash
sudo usermod -a -G spi,gpio $USER
# Logout and login again
```

### Display shows nothing

1. Check physical connections between HAT and board
2. Verify backlight is on (should see slight glow)
3. Try running with `sudo` (GPIO access requires root)
4. Lower SPI speed in script (change `spi_freq` to 1000000)

### Import errors

Make sure all dependencies are installed:
```bash
sudo pip3 install --upgrade gpiozero lgpio pillow spidev
```

## Project Structure

```
oPiTripleHatLCD/
├── README.md                          # This file
├── lib/                               # Orange Pi LCD driver libraries
│   ├── LCD_0inch96.py                 # 0.96" LCD driver (adapted for OPi)
│   ├── lcdconfig.py                   # GPIO/SPI config using gpiozero
│   └── __init__.py                    # Package init
├── examples/                          # Orange Pi example scripts
│   └── hello_world.py                 # Simple hello world demo
├── pic/                               # Image assets for demos
│   ├── LCD_0inch96.jpg                # Demo image 1
│   └── LCD_1inch3.jpg                 # Demo image 2
└── raspberryPi_TripleLCDHat_Demo/     # Original Raspberry Pi demo (reference)
    └── python/
        ├── lib/                       # Original RPi libraries
        ├── example/                   # Original RPi examples
        └── Font/                      # Font files for text rendering
```

## Advanced Usage

For more examples, see `raspberryPi_TripleLCDHat_Demo/python/example/`:
- `0inch96_spi0ce0.py` - First 0.96" display test
- `0inch96_spi0ce1.py` - Second 0.96" display test  
- `1inch3_spi1ce0.py` - 1.3" display test
- `double_0inch96_spi.py` - Both 0.96" displays simultaneously
- `CPU.py` - CPU info display

**Note**: Original examples are for Raspberry Pi - pin numbers may need adjustment for Orange Pi.

## License

Original code by Waveshare. Modifications for Orange Pi compatibility.

## Support

- Waveshare Wiki: https://www.waveshare.com/wiki/Zero_LCD_HAT_(A)
- Product Page: https://www.waveshare.com/zero-lcd-hat-a.htm
