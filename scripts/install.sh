#!/bin/bash

# ProxyVault Installation Script for Ubuntu 22.04/24.04
# Run as root: sudo bash install.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}ProxyVault Installation Script${NC}"
echo -e "${GREEN}================================${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Check Ubuntu version
if ! grep -q "Ubuntu" /etc/os-release; then
    echo -e "${YELLOW}Warning: This script is designed for Ubuntu. Other distributions may not work.${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}[1/8] Updating system packages...${NC}"
apt-get update -qq

echo -e "${GREEN}[2/8] Installing dependencies...${NC}"
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    unzip \
    iptables \
    openvpn \
    net-tools \
    iproute2

echo -e "${GREEN}[3/8] Installing Hysteria 2...${NC}"
if ! command -v hysteria &> /dev/null; then
    bash <(curl -fsSL https://get.hy2.sh/)
    echo -e "${GREEN}Hysteria 2 installed successfully${NC}"
else
    echo -e "${YELLOW}Hysteria already installed, skipping${NC}"
fi

echo -e "${GREEN}[4/8] Installing Xray-core (for VLESS)...${NC}"
if ! command -v xray &> /dev/null; then
    bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
    echo -e "${GREEN}Xray-core installed successfully${NC}"
else
    echo -e "${YELLOW}Xray already installed, skipping${NC}"
fi

echo -e "${GREEN}[5/8] Creating ProxyVault directories...${NC}"
mkdir -p /opt/proxyvault
mkdir -p /etc/proxyvault
mkdir -p /etc/hysteria
mkdir -p /etc/xray
mkdir -p /etc/openvpn/client
mkdir -p /var/log/proxyvault

echo -e "${GREEN}[6/8] Installing Python backend...${NC}"
cd /opt/proxyvault

# Copy backend files (assumes script is run from ProxyVault directory)
if [ -d "$(dirname "$0")/../backend" ]; then
    cp -r "$(dirname "$0")/../backend" /opt/proxyvault/
else
    echo -e "${YELLOW}Backend files not found. Cloning from GitHub...${NC}"
    # This will be updated with actual GitHub URL
    echo -e "${RED}Please manually copy backend files to /opt/proxyvault/backend${NC}"
fi

# Create Python virtual environment
python3 -m venv /opt/proxyvault/venv
source /opt/proxyvault/venv/bin/activate
pip install --upgrade pip
pip install -r /opt/proxyvault/backend/requirements.txt

echo -e "${GREEN}[7/8] Creating systemd service...${NC}"
cat > /etc/systemd/system/proxyvault.service << 'EOF'
[Unit]
Description=ProxyVault API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/proxyvault/backend
Environment="PATH=/opt/proxyvault/venv/bin"
ExecStart=/opt/proxyvault/venv/bin/python app.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable proxyvault
systemctl start proxyvault

echo -e "${GREEN}[8/8] Configuring firewall...${NC}"
# Allow API port
if command -v ufw &> /dev/null; then
    ufw allow 8000/tcp comment "ProxyVault API"
    echo -e "${GREEN}Firewall rule added for port 8000${NC}"
fi

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}\n"

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || echo "YOUR_SERVER_IP")

echo -e "${GREEN}ProxyVault is now running!${NC}\n"
echo -e "Access the admin panel at: ${YELLOW}http://${SERVER_IP}:8000${NC}"
echo -e "Default credentials:"
echo -e "  Username: ${YELLOW}admin${NC}"
echo -e "  Password: ${YELLOW}admin123${NC}"
echo -e "\n${RED}⚠️  IMPORTANT: Change the default password immediately!${NC}"
echo -e "Edit /opt/proxyvault/backend/.env and restart: ${YELLOW}systemctl restart proxyvault${NC}\n"

echo -e "Service management:"
echo -e "  Check status: ${YELLOW}systemctl status proxyvault${NC}"
echo -e "  View logs:    ${YELLOW}journalctl -u proxyvault -f${NC}"
echo -e "  Restart:      ${YELLOW}systemctl restart proxyvault${NC}\n"

echo -e "${GREEN}Next steps:${NC}"
echo -e "1. Access the admin panel and change default credentials"
echo -e "2. Configure Hysteria or VLESS proxy"
echo -e "3. Upload OpenVPN configuration (optional)"
echo -e "4. Enable traffic routing if using OpenVPN\n"

echo -e "For documentation, visit: ${YELLOW}https://github.com/YOUR_USERNAME/ProxyVault${NC}\n"
