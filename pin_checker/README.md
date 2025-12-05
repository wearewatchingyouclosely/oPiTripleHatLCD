# 🍊 Orange Pi Zero 2W GPIO Control Tool

**Super simple CLI tool for controlling GPIO pins on Orange Pi Zero 2W**

Control any GPIO pin with easy commands like `gpio_control.py --on 18` or use interactive mode for real-time testing!

## ⚡ Quick Start (Copy & Paste)

```bash
# 1. Download the tool
wget https://raw.githubusercontent.com/your-repo/pin_checker/gpio_control.py
chmod +x gpio_control.py

# 2. Test it works
python3 gpio_control.py --pinout

# 3. Control a pin (turn on pin 18)
python3 gpio_control.py --on 18

# 4. Interactive mode for testing
python3 gpio_control.py
```

## 🔧 Installation

### Option 1: One-Line Install
```bash
curl -sSL https://raw.githubusercontent.com/your-repo/install.sh | bash
```

### Option 2: Manual Install
```bash
# Make sure you're on Orange Pi Zero 2W with Armbian/Ubuntu
# Check GPIO system exists
ls /sys/class/gpio/

# Download script
wget https://raw.githubusercontent.com/your-repo/pin_checker/gpio_control.py
chmod +x gpio_control.py

# Test it
python3 gpio_control.py --help
```

### Option 3: Local Development
```bash
git clone https://github.com/your-repo/oPiTripleHatLCD.git
cd oPiTripleHatLCD/pin_checker/
python3 gpio_control.py
```

## 🎮 How to Use

### Interactive Mode (Easiest!)
Just run with no arguments for an easy interactive interface:

```bash
python3 gpio_control.py
```

Then type commands like:
- `on 18` - Turn on pin 18
- `off 18` - Turn off pin 18  
- `read 18` - Read pin 18 value
- `pinout` - Show all pins
- `help` - Show all commands

### Command Line Mode
Perfect for scripts and automation:

```bash
# Turn pin ON
python3 gpio_control.py --on 18

# Turn pin OFF  
python3 gpio_control.py --off 18

# Set pin to specific value
python3 gpio_control.py --set 18 1    # HIGH
python3 gpio_control.py --set 18 0    # LOW

# Read pin value
python3 gpio_control.py --read 18

# Blink pin 5 times
python3 gpio_control.py --blink 18 5

# Show pinout
python3 gpio_control.py --pinout

# List controllable pins
python3 gpio_control.py --list
```

## 📍 Pin Reference

**Orange Pi Zero 2W GPIO Pins (Physical → GPIO Number):**

| Physical Pin | GPIO | Function | Physical Pin | GPIO | Function |
|--------------|------|----------|--------------|------|----------|
| 3 | 264 | SDA.1 | 5 | 263 | SCL.1 |
| 7 | 269 | PWM3 | 8 | 224 | TXD.0 |
| 10 | 225 | RXD.0 | 11 | 226 | TXD.5 |
| 12 | 257 | PI01 | 13 | 227 | RXD.5 |
| 15 | 261 | TXD.2 | 16 | 270 | PWM4 |
| 18 | 228 | PH04 | 19 | 231 | MOSI.1 |
| 21 | 232 | MISO.1 | 22 | 262 | RXD.2 |
| 23 | 230 | SCLK.1 | 24 | 229 | CE.0 |
| 26 | 233 | CE.1 | 27 | 266 | SDA.2 |
| 28 | 265 | SCL.2 | 29 | 256 | PI00 |
| 31 | 271 | PI15 | 32 | 267 | PWM1 |
| 33 | 268 | PI12 | 35 | 258 | PI02 |
| 36 | 76 | PC12 | 37 | 272 | PI16 |
| 38 | 260 | PI04 | 40 | 259 | PI03 |

**Power/Ground pins (1,2,4,6,9,14,17,20,25,30,34,39) cannot be controlled.**

## 🚀 Examples

### Test Your HAT Connection
```bash
# Interactive testing
python3 gpio_control.py
GPIO> on 18     # Turn on pin 18
GPIO> read 22   # Read pin 22  
GPIO> off 18    # Turn off pin 18
GPIO> quit
```

### Blink an LED
```bash
# Connect LED to pin 18 and ground
python3 gpio_control.py --blink 18 10
```

### Script Integration
```bash
#!/bin/bash
# Turn on multiple pins
python3 gpio_control.py --on 18
python3 gpio_control.py --on 22
python3 gpio_control.py --on 24

# Wait 5 seconds
sleep 5

# Turn off all pins
python3 gpio_control.py --off 18
python3 gpio_control.py --off 22  
python3 gpio_control.py --off 24
```

## 🛠️ Troubleshooting

### Permission Denied
```bash
# Add your user to gpio group
sudo usermod -a -G gpio $USER
# Log out and back in

# Or run with sudo (not recommended for regular use)
sudo python3 gpio_control.py --on 18
```

### GPIO Not Found
```bash
# Make sure you're on Orange Pi Zero 2W
uname -a

# Check GPIO system exists
ls /sys/class/gpio/
# Should show: export, gpiochip0, gpiochip352, unexport
```

### Pin Already in Use
```bash
# Some pins might be used by system services
# Try a different pin, or check what's using it:
lsof /dev/gpio*
```

### Wrong Pin Number
```bash
# Show valid pins
python3 gpio_control.py --list

# Show full pinout
python3 gpio_control.py --pinout
```

## 🔍 Testing Your Setup

### Quick Hardware Test
1. Connect an LED between pin 18 and ground (with resistor)
2. Run: `python3 gpio_control.py --blink 18 5`
3. LED should blink 5 times

### HAT Compatibility Test
1. Connect your Raspberry Pi HAT
2. Check pinout: `python3 gpio_control.py --pinout`
3. Test each pin your HAT uses:
   ```bash
   python3 gpio_control.py
   GPIO> on 18    # Test pin 18
   GPIO> on 22    # Test pin 22
   GPIO> read 24  # Read pin 24
   ```

## 💡 Pro Tips

### Batch Operations
```bash
# Turn on multiple pins at once
for pin in 18 22 24; do
    python3 gpio_control.py --on $pin
done
```

### Check Pin Status
```bash
# In interactive mode, use 'status' to see active pins
python3 gpio_control.py
GPIO> on 18
GPIO> on 22  
GPIO> status
# Shows: EXPORTED PINS: [228, 262]
```

### Safe Testing
- Always check the pinout before connecting hardware
- Start with simple LED tests before connecting expensive components  
- Use the interactive mode for experimentation
- Command line mode for automation and scripts

## ⚠️ Important Notes

- **Physical pin numbers** (1-40) are used, not GPIO numbers
- **Power pins** (3.3V, 5V, GND) cannot be controlled
- **Clean up** happens automatically when exiting
- **Root access** may be needed for first-time GPIO access
- **Compatible** with Orange Pi Zero 2W running Armbian/Ubuntu

## 🤝 Support

- **Pin not working?** Check if it's a power/ground pin
- **Permission issues?** Add your user to the `gpio` group  
- **Hardware problems?** Test with a simple LED first
- **Software issues?** Make sure you're on Orange Pi Zero 2W

---

**Made for Orange Pi Zero 2W | Simple • Fast • Reliable**