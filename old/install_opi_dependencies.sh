#!/bin/bash
# Orange Pi Zero 2W LCD HAT Setup Script
# Installs all required dependencies for OPi.GPIO-based LCD control

set -e  # Exit on any error

echo "=================================================="
echo "Orange Pi Zero 2W LCD HAT Setup"
echo "Installing OPi.GPIO and dependencies"
echo "=================================================="

# Check if running on ARM (Orange Pi)
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" && "$ARCH" != "armv7l" && "$ARCH" != "armv6l" ]]; then
    echo "⚠️  Warning: This script is designed for Orange Pi (ARM architecture)"
    echo "   Current architecture: $ARCH"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

echo ""
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo ""
echo "2. Installing system dependencies..."
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv \
    git \
    build-essential \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7 \
    libtiff5 \
    zlib1g-dev \
    libffi-dev \
    libssl-dev

echo ""
echo "3. Installing Python packages..."

# Install core GPIO library
echo "   Installing OPi.GPIO..."
pip3 install --user OPi.GPIO

# Install SPI library
echo "   Installing spidev..."
pip3 install --user spidev

# Install image processing
echo "   Installing Pillow (PIL)..."
pip3 install --user Pillow

# Install numpy
echo "   Installing numpy..."
pip3 install --user numpy

echo ""
echo "4. Checking SPI configuration..."
if [ -e "/dev/spidev1.0" ]; then
    echo "   ✅ SPI device /dev/spidev1.0 found - SPI is enabled!"
else
    echo "   ❌ SPI device /dev/spidev1.0 not found"
    echo ""
    echo "   To enable SPI:"
    echo "   1. Run: sudo armbian-config"
    echo "   2. Navigate to: System → Kernel → DTO001"
    echo "   3. Enable SPI and reboot"
    echo ""
    echo "   After reboot, run this script again to verify."
fi

echo ""
echo "5. Checking GPIO permissions..."
if groups | grep -q "gpio"; then
    echo "   ✅ User is in GPIO group"
else
    echo "   Adding user to GPIO group..."
    sudo usermod -a -G gpio $USER
    echo "   ⚠️  You need to log out and log back in for group changes to take effect"
fi

echo ""
echo "6. Testing Python imports..."
python3 -c "
import sys
try:
    import OPi.GPIO as GPIO
    print('   ✅ OPi.GPIO import successful')
except ImportError as e:
    print(f'   ❌ OPi.GPIO import failed: {e}')
    sys.exit(1)

try:
    import spidev
    print('   ✅ spidev import successful')
except ImportError as e:
    print(f'   ❌ spidev import failed: {e}')
    sys.exit(1)

try:
    from PIL import Image
    print('   ✅ PIL (Pillow) import successful')
except ImportError as e:
    print(f'   ❌ PIL import failed: {e}')
    sys.exit(1)

try:
    import numpy
    print('   ✅ numpy import successful')
except ImportError as e:
    print(f'   ❌ numpy import failed: {e}')
    sys.exit(1)

print('   ✅ All Python libraries imported successfully!')
"

echo ""
echo "7. Creating project structure..."
mkdir -p ~/lcd_hat_test/{lib,examples}
echo "   ✅ Directories created: ~/lcd_hat_test/{lib,examples}"

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo ""
echo "Next Steps:"
echo "1. Copy the project files to ~/lcd_hat_test/"
echo "   - lib/lcdconfig_opi.py"
echo "   - lib/LCD_0inch96_opi.py" 
echo "   - examples/hello_world_opi.py"
echo "   - examples/test_opi_gpio.py"
echo ""
echo "2. If SPI was not enabled, run:"
echo "   sudo armbian-config"
echo "   → System → Kernel → DTO001 → Enable"
echo "   → Reboot"
echo ""
echo "3. Test GPIO functionality:"
echo "   cd ~/lcd_hat_test"
echo "   python3 examples/test_opi_gpio.py"
echo ""
echo "4. Run the Hello World demo:"
echo "   python3 examples/hello_world_opi.py"
echo ""
echo "🎉 Your Orange Pi Zero 2W is ready for LCD HAT testing!"
echo "=================================================="