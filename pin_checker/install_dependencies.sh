#!/bin/bash
# Orange Pi Zero 2W GPIO Pin Controller - Dependency Installer
# This script installs all required dependencies for the GPIO pin controller

set -e  # Exit on any error

echo "🍊 Orange Pi Zero 2W GPIO Pin Controller Setup"
echo "============================================="

# Check if running on supported architecture
ARCH=$(uname -m)
echo "🔍 Detected architecture: $ARCH"

if [[ "$ARCH" != "aarch64" && "$ARCH" != "armv7l" && "$ARCH" != "armv6l" ]]; then
    echo "⚠️  Warning: This is designed for Orange Pi (ARM architecture)"
    echo "   You can still install for testing, but GPIO control won't work"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Check if we're on Orange Pi
if [[ -f /etc/armbian-release ]]; then
    source /etc/armbian-release
    echo "✅ Detected Armbian OS"
    echo "   Board: $BOARD"
    echo "   Version: $VERSION"
elif [[ -f /proc/device-tree/model ]]; then
    MODEL=$(cat /proc/device-tree/model)
    echo "✅ Board model: $MODEL"
else
    echo "ℹ️  Could not detect board type"
fi

echo ""
echo "1️⃣ Updating system packages..."
sudo apt update

echo ""
echo "2️⃣ Installing Python and development tools..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-tk \
    python3-dev \
    python3-setuptools \
    git

echo ""
echo "3️⃣ Installing Python GUI dependencies..."
# Tkinter should be included with python3-tk, but let's ensure all GUI libs are present
sudo apt install -y \
    python3-pil \
    python3-pil.imagetk

echo ""
echo "4️⃣ Installing GPIO libraries..."

# Try to install OPi.GPIO (preferred)
echo "   Installing OPi.GPIO (preferred library)..."
if pip3 install --user OPi.GPIO; then
    echo "   ✅ OPi.GPIO installed successfully"
else
    echo "   ⚠️  OPi.GPIO installation failed, will use fallback sysfs method"
fi

# Install other useful GPIO libraries as alternatives
echo "   Installing additional GPIO tools..."
pip3 install --user gpiozero 2>/dev/null || echo "   ℹ️  gpiozero not available for this platform"

echo ""
echo "5️⃣ Setting up GPIO permissions..."

# Check if gpio group exists
if getent group gpio > /dev/null; then
    echo "   ✅ GPIO group exists"
    
    # Add user to gpio group
    if groups $USER | grep -q gpio; then
        echo "   ✅ User $USER is already in gpio group"
    else
        echo "   Adding user $USER to gpio group..."
        sudo usermod -a -G gpio $USER
        echo "   ⚠️  You need to log out and log back in for group changes to take effect"
        echo "   Or run: newgrp gpio"
    fi
else
    echo "   ℹ️  GPIO group doesn't exist, will rely on sudo for GPIO access"
fi

echo ""
echo "6️⃣ Testing Python imports..."

python3 -c "
import sys
import os

print('Python version:', sys.version)

try:
    import tkinter as tk
    print('✅ tkinter (GUI) - OK')
except ImportError as e:
    print('❌ tkinter (GUI) - FAILED:', e)
    sys.exit(1)

try:
    import OPi.GPIO as GPIO
    print('✅ OPi.GPIO - OK')
except ImportError:
    print('⚠️  OPi.GPIO not available, will use fallback sysfs method')

# Test if we have GPIO access
gpio_available = False
if os.path.exists('/sys/class/gpio'):
    print('✅ GPIO sysfs interface - Available')
    gpio_available = True
else:
    print('❌ GPIO sysfs interface - Not found')

if gpio_available:
    print('✅ GPIO hardware interface detected')
else:
    print('⚠️  No GPIO hardware interface found')
"

echo ""
echo "7️⃣ Creating launcher script..."

cat > gpio_launcher.sh << 'EOF'
#!/bin/bash
# GPIO Pin Controller Launcher

echo "🍊 Starting Orange Pi Zero 2W GPIO Pin Controller..."

# Check if we're in the right directory
if [[ ! -f "gpio_pin_controller.py" ]]; then
    echo "❌ Error: gpio_pin_controller.py not found"
    echo "Please run this script from the pin_checker directory"
    exit 1
fi

# Try to run with current user first
if python3 gpio_pin_controller.py 2>/dev/null; then
    echo "✅ GPIO controller ran successfully"
elif python3 gpio_pin_controller.py; then
    echo "✅ GPIO controller ran with warnings"
else
    echo ""
    echo "⚠️  GPIO controller failed to start normally"
    echo "This might be due to permissions. Trying with sudo..."
    echo "Note: You may need to install packages for root user too"
    echo ""
    sudo python3 gpio_pin_controller.py
fi
EOF

chmod +x gpio_launcher.sh

echo ""
echo "8️⃣ Testing command-line GPIO tools..."
echo "   Running quick GPIO library test..."

if python3 test_pins.py --list > /dev/null 2>&1; then
    echo "   ✅ Command-line GPIO tools working"
else
    echo "   ⚠️  Command-line GPIO tools need debugging"
fi

echo ""
echo "=================================================="
echo "🎉 Installation Complete!"
echo ""
echo "📝 What was installed:"
echo "  ✅ Python 3 and Tkinter (GUI framework)"  
echo "  ✅ OPi.GPIO library (if compatible)"
echo "  ✅ Fallback sysfs GPIO control"
echo "  ✅ GPIO permissions configured"
echo "  ✅ Test scripts and launcher"
echo ""
echo "🚀 How to run:"
echo ""
echo "  1. GUI Application:"
echo "     ./gpio_launcher.sh"
echo "     # OR #"
echo "     python3 gpio_pin_controller.py"
echo ""
echo "  2. Command-line Testing:"
echo "     python3 test_pins.py --list          # List all pins"
echo "     python3 test_pins.py --pin 7         # Test pin 7"
echo "     python3 test_pins.py --quick         # Quick test"
echo "     python3 test_pins.py                 # Interactive mode"
echo ""
echo "⚠️  Important Notes:"
echo "  - If you were added to gpio group, log out and back in"
echo "  - Some operations may require sudo on first run"
echo "  - Always cleanup GPIO pins when done (app does this automatically)"
echo "  - Be careful with GPIO pins - incorrect use can damage hardware"
echo ""
echo "📖 For detailed usage instructions, see README.md"
echo "=================================================="