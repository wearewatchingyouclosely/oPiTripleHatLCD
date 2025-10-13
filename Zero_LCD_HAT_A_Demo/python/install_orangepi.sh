#!/bin/bash
# Orange Pi Zero 2W LCD HAT Installation Script
# Run with: sudo bash install_orangepi.sh

echo "========================================="
echo "Orange Pi Zero 2W LCD HAT Setup Script"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "Updating system packages..."
apt update

echo "Installing required Python packages..."
apt install -y python3-pip python3-dev python3-pil python3-numpy

echo "Installing SPI development packages..."
apt install -y python3-spidev

echo "Installing Orange Pi GPIO library..."
pip3 install OPi.GPIO

# Alternative GPIO libraries as fallback
echo "Installing alternative GPIO libraries..."
pip3 install RPi.GPIO || echo "RPi.GPIO installation failed (expected on some systems)"
pip3 install gpiozero || echo "gpiozero installation failed"

echo "Enabling SPI interface..."
# Check if orangepi-config exists
if command -v orangepi-config &> /dev/null; then
    echo "Please run 'sudo orangepi-config' and enable SPI under System -> Hardware -> spi-spidev"
    echo "Then reboot your system."
else
    echo "orangepi-config not found. Trying alternative method..."
    
    # Try to load SPI modules
    modprobe spi-sun50i-h616 2>/dev/null || modprobe spi-sun8i-h3 2>/dev/null || echo "Could not load SPI module automatically"
    modprobe spidev 2>/dev/null || echo "Could not load spidev module"
    
    # Add to modules to load at boot
    echo "spi-sun50i-h616" >> /etc/modules 2>/dev/null || echo "spi-sun8i-h3" >> /etc/modules 2>/dev/null
    echo "spidev" >> /etc/modules
fi

echo "Checking SPI devices..."
ls -la /dev/spi* 2>/dev/null || echo "No SPI devices found yet. You may need to enable SPI and reboot."

echo "Setting up udev rules for SPI access..."
cat > /etc/udev/rules.d/50-spi.rules << EOF
SUBSYSTEM=="spidev", GROUP="spi", MODE="0664"
SUBSYSTEM=="spidev", GROUP="gpio", MODE="0664"
EOF

# Add user to gpio group if it exists
if getent group gpio > /dev/null 2>&1; then
    usermod -a -G gpio $SUDO_USER 2>/dev/null
    echo "Added user to gpio group"
fi

# Create spi group if it doesn't exist and add user
if ! getent group spi > /dev/null 2>&1; then
    groupadd spi
fi
usermod -a -G spi $SUDO_USER 2>/dev/null
echo "Added user to spi group"

echo "Installation completed!"
echo ""
echo "========================================="
echo "IMPORTANT: Next steps"
echo "========================================="
echo "1. Reboot your Orange Pi Zero 2W"
echo "2. After reboot, check if SPI is enabled:"
echo "   ls -la /dev/spi*"
echo "3. You should see devices like /dev/spidev1.0"
echo "4. Test the demo:"
echo "   cd example"
echo "   sudo python3 orangepi_demo.py"
echo ""
echo "If SPI devices are not present after reboot:"
echo "- Run: sudo orangepi-config"
echo "- Go to System -> Hardware -> spi-spidev"
echo "- Enable it and reboot"
echo "========================================="