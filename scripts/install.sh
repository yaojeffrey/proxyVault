#!/bin/bash

# ProxyVault Installation Script for Ubuntu 22.04/24.04
# Run from repository root: cd proxyVault && sudo bash scripts/install.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}ProxyVault Installation Script${NC}"
echo -e "${GREEN}================================${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERROR: Please run as root or with sudo${NC}"
    echo -e "${YELLOW}Usage: sudo bash scripts/install.sh${NC}"
    exit 1
fi

# Detect repository root (where script is being run from)
# User should run: cd proxyVault && sudo bash scripts/install.sh
REPO_ROOT="$(pwd)"
SCRIPT_DIR="$REPO_ROOT/scripts"

echo -e "${BLUE}Checking repository structure...${NC}"
echo "Repository root: $REPO_ROOT"

# Verify we're in the right place
if [ ! -f "$REPO_ROOT/README.md" ] || [ ! -d "$REPO_ROOT/backend" ] || [ ! -d "$REPO_ROOT/frontend" ]; then
    echo -e "${RED}ERROR: Not running from repository root!${NC}"
    echo -e "${YELLOW}Please run this script like:${NC}"
    echo -e "${YELLOW}  cd ~/proxyVault${NC}"
    echo -e "${YELLOW}  sudo bash scripts/install.sh${NC}"
    echo ""
    echo -e "${RED}Required files not found:${NC}"
    [ ! -f "$REPO_ROOT/README.md" ] && echo "  - README.md"
    [ ! -d "$REPO_ROOT/backend" ] && echo "  - backend/"
    [ ! -d "$REPO_ROOT/frontend" ] && echo "  - frontend/"
    exit 1
fi

echo -e "${GREEN}✓ Repository structure verified${NC}\n"

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
    openssl \
    net-tools \
    iproute2

echo -e "${GREEN}[3/8] Installing Hysteria 2...${NC}"
if ! command -v hysteria &> /dev/null; then
    bash <(curl -fsSL https://get.hy2.sh/)
    echo -e "${GREEN}✓ Hysteria 2 installed successfully${NC}"
else
    echo -e "${YELLOW}Hysteria already installed, skipping${NC}"
fi

echo -e "${GREEN}[4/8] Installing Xray-core (for VLESS)...${NC}"
if ! command -v xray &> /dev/null; then
    bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
    echo -e "${GREEN}✓ Xray-core installed successfully${NC}"
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

# Copy backend files
echo "Copying backend files from $REPO_ROOT/backend"
cp -r "$REPO_ROOT/backend" /opt/proxyvault/
echo -e "${GREEN}✓ Backend files copied${NC}"

# Copy frontend files
echo "Copying frontend files from $REPO_ROOT/frontend"
cp -r "$REPO_ROOT/frontend" /opt/proxyvault/
echo -e "${GREEN}✓ Frontend files copied${NC}"

# Verify files copied
if [ ! -f "/opt/proxyvault/backend/requirements.txt" ]; then
    echo -e "${RED}ERROR: Backend files not copied correctly${NC}"
    exit 1
fi

if [ ! -f "/opt/proxyvault/frontend/index.html" ]; then
    echo -e "${RED}ERROR: Frontend files not copied correctly${NC}"
    exit 1
fi

# Create Python virtual environment
echo "Creating Python virtual environment..."
cd /opt/proxyvault/backend
python3 -m venv /opt/proxyvault/venv

echo "Installing Python packages..."
/opt/proxyvault/venv/bin/pip install --upgrade pip -q
/opt/proxyvault/venv/bin/pip install -r requirements.txt -q

echo -e "${GREEN}✓ Python backend installed successfully${NC}"

echo -e "${GREEN}[7/8] Creating systemd service...${NC}"
cat > /etc/systemd/system/proxyvault.service << 'EOF'
[Unit]
Description=ProxyVault API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/proxyvault/backend
Environment="PATH=/opt/proxyvault/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
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

# Wait a moment for service to start
sleep 2

# Check if service started successfully
if systemctl is-active --quiet proxyvault; then
    echo -e "${GREEN}✓ ProxyVault service started successfully${NC}"
else
    echo -e "${RED}ERROR: ProxyVault service failed to start${NC}"
    echo -e "${YELLOW}Checking logs:${NC}"
    journalctl -u proxyvault -n 20 --no-pager
    exit 1
fi

echo -e "${GREEN}[8/8] Configuring firewall...${NC}"
# Allow API port
if command -v ufw &> /dev/null; then
    ufw allow 8000/tcp comment "ProxyVault API"
    echo -e "${GREEN}✓ Firewall rule added for port 8000${NC}"
else
    echo -e "${YELLOW}UFW not found, skipping firewall configuration${NC}"
fi

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1 > /dev/null
if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf 2>/dev/null; then
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
fi
echo -e "${GREEN}✓ IP forwarding enabled${NC}"

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")

echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}\n"

echo -e "${GREEN}ProxyVault is now running!${NC}\n"
echo -e "📊 Service Status:"
echo -e "  ProxyVault: ${GREEN}Running${NC}"
echo -e "  Hysteria:   $(command -v hysteria &> /dev/null && echo -e '${GREEN}Installed${NC}' || echo -e '${RED}Not Installed${NC}')"
echo -e "  Xray:       $(command -v xray &> /dev/null && echo -e '${GREEN}Installed${NC}' || echo -e '${RED}Not Installed${NC}')"
echo -e "  OpenVPN:    $(command -v openvpn &> /dev/null && echo -e '${GREEN}Installed${NC}' || echo -e '${RED}Not Installed${NC}')"
echo ""
echo -e "🌐 Access via SSH Tunnel:"
echo -e "  ${YELLOW}ssh -L 8000:localhost:8000 ubuntu@${SERVER_IP}${NC}"
echo -e "  Then open: ${YELLOW}http://localhost:8000/static/index.html${NC}"
echo ""
echo -e "🔑 Default Credentials:"
echo -e "  Username: ${YELLOW}admin${NC}"
echo -e "  Password: ${YELLOW}admin123${NC}"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Change the default password!${NC}"
echo -e "  Edit: ${YELLOW}/opt/proxyvault/backend/.env${NC}"
echo -e "  Then: ${YELLOW}sudo systemctl restart proxyvault${NC}\n"

echo -e "📝 Useful Commands:"
echo -e "  Status:  ${YELLOW}sudo systemctl status proxyvault${NC}"
echo -e "  Logs:    ${YELLOW}sudo journalctl -u proxyvault -f${NC}"
echo -e "  Restart: ${YELLOW}sudo systemctl restart proxyvault${NC}\n"

echo -e "📚 Documentation: ${YELLOW}https://github.com/yaojeffrey/proxyVault${NC}\n"

echo -e "${GREEN}🎉 Ready to use! Access the admin panel via SSH tunnel.${NC}\n"
