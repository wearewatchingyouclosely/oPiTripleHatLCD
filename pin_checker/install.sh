#!/bin/bash
# Orange Pi Zero 2W GPIO Control Tool - Easy Installer

set -e

echo "🍊 Orange Pi Zero 2W GPIO Control Tool Installer"
echo "================================================"

# Check if running on ARM (Orange Pi)
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" && "$ARCH" != "armv7l" && "$ARCH" != "armv6l" ]]; then
    echo "⚠️  Warning: This tool is designed for Orange Pi (ARM architecture)"
    echo "   Current architecture: $ARCH"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

echo ""
echo "1. Checking system requirements..."

# Check for GPIO support
if [ ! -d "/sys/class/gpio" ]; then
    echo "❌ Error: GPIO sysfs interface not found"
    echo "   Make sure you're running on Orange Pi with GPIO support"
    exit 1
fi

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Installing..."
    sudo apt update
    sudo apt install -y python3
fi

echo "✅ System requirements OK"

echo ""
echo "2. Setting up GPIO permissions..."

# Add user to gpio group if it exists
if getent group gpio > /dev/null 2>&1; then
    if ! groups | grep -q "gpio"; then
        echo "   Adding user to GPIO group..."
        sudo usermod -a -G gpio $USER
        echo "   ⚠️  You'll need to log out and back in for group changes to take effect"
    else
        echo "   ✅ User already in GPIO group"
    fi
else
    echo "   ⚠️  GPIO group not found, you may need to run with sudo"
fi

echo ""
echo "3. Installing GPIO control tool..."

# Create local bin directory if it doesn't exist
mkdir -p ~/.local/bin

# Download the tool (for now, copy from local files)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/gpio_control.py" ]; then
    cp "$SCRIPT_DIR/gpio_control.py" ~/.local/bin/
    chmod +x ~/.local/bin/gpio_control.py
    echo "   ✅ Installed to ~/.local/bin/gpio_control.py"
else
    echo "   ❌ gpio_control.py not found in $SCRIPT_DIR"
    exit 1
fi

echo ""
echo "4. Setting up PATH..."

# Add ~/.local/bin to PATH if not already there
if ! echo $PATH | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "   ✅ Added ~/.local/bin to PATH in ~/.bashrc"
    echo "   ⚠️  Run 'source ~/.bashrc' or start a new terminal to use 'gpio_control.py' command"
else
    echo "   ✅ ~/.local/bin already in PATH"
fi

echo ""
echo "5. Testing installation..."

cd ~/.local/bin
if python3 gpio_control.py --help > /dev/null 2>&1; then
    echo "   ✅ GPIO control tool working correctly"
else
    echo "   ❌ Tool test failed"
    exit 1
fi

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "Quick Start:"
echo "  # Show pinout"
echo "  python3 ~/.local/bin/gpio_control.py --pinout"
echo ""
echo "  # Interactive mode (easiest)"  
echo "  python3 ~/.local/bin/gpio_control.py"
echo ""
echo "  # Turn pin 18 on"
echo "  python3 ~/.local/bin/gpio_control.py --on 18"
echo ""
echo "  # After sourcing ~/.bashrc, you can use:"
echo "  gpio_control.py --help"
echo ""

# Test a simple GPIO operation if possible
echo "Testing GPIO access..."
if python3 gpio_control.py --list > /dev/null 2>&1; then
    echo "✅ GPIO system accessible"
    echo ""
    echo "🚀 Ready to control GPIO pins!"
    echo "   Try: python3 ~/.local/bin/gpio_control.py --pinout"
else
    echo "⚠️  GPIO access may require 'sudo' or group membership"
    echo "   Try: sudo python3 ~/.local/bin/gpio_control.py --pinout"
fi

echo ""
echo "📖 Full documentation in README.md"
echo "🐛 Issues? Check the troubleshooting section in README.md"