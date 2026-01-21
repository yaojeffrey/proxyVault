# ProxyVault Setup Guide

## Quick Setup (Ubuntu 22.04/24.04)

### 1. One-Line Installation

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ProxyVault/main/scripts/install.sh | sudo bash
```

### 2. Access Admin Panel

```
http://YOUR_SERVER_IP:8000
Username: admin
Password: admin123
```

⚠️ **Change default credentials immediately!**

---

## Manual Setup

### Prerequisites

- Ubuntu 22.04 or 24.04 LTS
- Root access (sudo)
- Minimum 1GB RAM, 10GB disk
- Public IP address

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ProxyVault.git
cd ProxyVault
```

### Step 2: Run Installation Script

```bash
sudo bash scripts/install.sh
```

The script will:
- Install system dependencies
- Install Hysteria 2
- Install Xray-core (for VLESS)
- Install OpenVPN
- Set up Python backend
- Create systemd service
- Configure firewall

### Step 3: Configure Environment

```bash
cd /opt/proxyvault/backend
sudo cp .env.example .env
sudo nano .env
```

Change at minimum:
```env
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_secure_password
```

### Step 4: Restart Service

```bash
sudo systemctl restart proxyvault
```

### Step 5: Access Admin Panel

Open browser and navigate to:
```
http://YOUR_SERVER_IP:8000
```

---

## Configuration Examples

### Hysteria 2 Setup

1. Navigate to **Hysteria** tab
2. Set port (default: 36712)
3. Generate password
4. Optional: Add obfuscation password
5. Click **Save Configuration**
6. Click **Start**

**Client Configuration:**
```yaml
server: YOUR_SERVER_IP:36712
auth: YOUR_PASSWORD
bandwidth:
  up: 100 mbps
  down: 100 mbps
socks5:
  listen: 127.0.0.1:1080
http:
  listen: 127.0.0.1:8080
```

### VLESS + Reality Setup

1. Navigate to **VLESS** tab
2. Set port (default: 8443)
3. Click **Generate UUID**
4. Set Reality destination (e.g., www.microsoft.com:443)
5. Click **Generate New Keys**
6. Click **Save Configuration**
7. Click **Start**

**Client Configuration (v2rayN/Nekoray):**
```
Protocol: VLESS
Address: YOUR_SERVER_IP
Port: 8443
UUID: [your-generated-uuid]
Flow: xtls-rprx-vision
Network: tcp
Security: reality
SNI: www.microsoft.com
Public Key: [from web UI]
Short ID: (leave empty)
```

### OpenVPN Integration

1. Navigate to **OpenVPN** tab
2. Upload your .ovpn file OR paste content
3. Enter username/password if required
4. Click **Save & Connect**

### Enable Traffic Routing

1. Ensure OpenVPN is connected (green status)
2. Navigate to **Routing** tab
3. Click **Enable Routing**
4. All proxy traffic now routes through OpenVPN!

---

## Firewall Configuration

### Open Required Ports

```bash
# ProxyVault API
sudo ufw allow 8000/tcp comment "ProxyVault API"

# Hysteria
sudo ufw allow 36712/tcp comment "Hysteria"
sudo ufw allow 36712/udp comment "Hysteria"

# VLESS
sudo ufw allow 8443/tcp comment "VLESS"

# Enable firewall
sudo ufw enable
```

### Close Admin Panel to Public (Recommended)

If you only need local access:
```bash
# Delete public rule
sudo ufw delete allow 8000/tcp

# Allow only from specific IP
sudo ufw allow from YOUR_HOME_IP to any port 8000
```

Or use SSH tunnel:
```bash
ssh -L 8000:localhost:8000 user@YOUR_SERVER_IP
# Then access: http://localhost:8000
```

---

## Service Management

### Check Service Status

```bash
# ProxyVault API
sudo systemctl status proxyvault

# Hysteria
sudo systemctl status hysteria-server

# VLESS (Xray)
sudo systemctl status xray

# OpenVPN
sudo systemctl status openvpn-client@client
```

### View Logs

```bash
# ProxyVault
sudo journalctl -u proxyvault -f

# Hysteria
sudo journalctl -u hysteria-server -f

# VLESS
sudo journalctl -u xray -f

# OpenVPN
sudo journalctl -u openvpn-client@client -f
```

### Restart Services

```bash
sudo systemctl restart proxyvault
sudo systemctl restart hysteria-server
sudo systemctl restart xray
sudo systemctl restart openvpn-client@client
```

---

## Troubleshooting

### Admin Panel Not Accessible

1. Check if service is running:
```bash
sudo systemctl status proxyvault
```

2. Check if port is open:
```bash
sudo netstat -tlnp | grep 8000
```

3. Check firewall:
```bash
sudo ufw status
```

4. View logs:
```bash
sudo journalctl -u proxyvault -n 50
```

### Hysteria Not Starting

1. Check configuration:
```bash
sudo cat /etc/hysteria/config.yaml
```

2. Test manually:
```bash
sudo hysteria server --config /etc/hysteria/config.yaml
```

3. Check logs:
```bash
sudo journalctl -u hysteria-server -n 50
```

### VLESS Not Starting

1. Check configuration:
```bash
sudo cat /etc/xray/config.json
```

2. Validate JSON:
```bash
sudo xray -test -config /etc/xray/config.json
```

3. Check logs:
```bash
sudo journalctl -u xray -n 50
```

### OpenVPN Not Connecting

1. Check configuration:
```bash
sudo cat /etc/openvpn/client/client.conf
```

2. Test manually:
```bash
sudo openvpn --config /etc/openvpn/client/client.conf
```

3. Check logs:
```bash
sudo journalctl -u openvpn-client@client -n 50
```

### Traffic Routing Not Working

1. Check if OpenVPN is connected:
```bash
ip a show tun0
```

2. Check iptables rules:
```bash
sudo iptables -t nat -L -n -v
sudo iptables -t mangle -L -n -v
```

3. Check IP forwarding:
```bash
sysctl net.ipv4.ip_forward
```

4. Test routing:
```bash
# Check routing tables
ip route show table 100
ip rule list
```

---

## Security Best Practices

1. **Change default credentials immediately**
2. **Use strong passwords** (16+ characters)
3. **Enable firewall** and only open required ports
4. **Use SSH keys** instead of passwords
5. **Keep system updated**: `sudo apt update && sudo apt upgrade`
6. **Restrict admin panel access** to specific IPs
7. **Use HTTPS** for admin panel (add nginx reverse proxy)
8. **Regular backups** of configurations
9. **Monitor logs** for suspicious activity
10. **Disable root SSH**: `PermitRootLogin no` in `/etc/ssh/sshd_config`

---

## Performance Tuning

### Increase Connection Limits

```bash
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216
sudo sysctl -w net.ipv4.tcp_rmem='4096 87380 16777216'
sudo sysctl -w net.ipv4.tcp_wmem='4096 65536 16777216'
```

Make permanent:
```bash
sudo nano /etc/sysctl.conf
# Add above lines
sudo sysctl -p
```

### BBR Congestion Control

```bash
sudo sysctl -w net.core.default_qdisc=fq
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr
```

---

## Backup & Restore

### Backup

```bash
# Create backup directory
mkdir ~/proxyvault-backup

# Backup configurations
sudo cp /etc/hysteria/config.yaml ~/proxyvault-backup/
sudo cp /etc/xray/config.json ~/proxyvault-backup/
sudo cp /etc/openvpn/client/client.conf ~/proxyvault-backup/
sudo cp /opt/proxyvault/backend/.env ~/proxyvault-backup/

# Create archive
tar -czf proxyvault-backup-$(date +%Y%m%d).tar.gz ~/proxyvault-backup/
```

### Restore

```bash
# Extract backup
tar -xzf proxyvault-backup-YYYYMMDD.tar.gz

# Restore configurations
sudo cp ~/proxyvault-backup/config.yaml /etc/hysteria/
sudo cp ~/proxyvault-backup/config.json /etc/xray/
sudo cp ~/proxyvault-backup/client.conf /etc/openvpn/client/
sudo cp ~/proxyvault-backup/.env /opt/proxyvault/backend/

# Restart services
sudo systemctl restart proxyvault hysteria-server xray openvpn-client@client
```

---

## Uninstallation

```bash
# Stop and disable services
sudo systemctl stop proxyvault hysteria-server xray openvpn-client@client
sudo systemctl disable proxyvault hysteria-server xray openvpn-client@client

# Remove systemd service files
sudo rm /etc/systemd/system/proxyvault.service

# Remove application files
sudo rm -rf /opt/proxyvault
sudo rm -rf /etc/proxyvault
sudo rm -rf /etc/hysteria
sudo rm -rf /etc/xray
sudo rm -rf /etc/openvpn/client

# Remove binaries (optional)
sudo rm /usr/local/bin/hysteria
sudo rm /usr/local/bin/xray

# Reload systemd
sudo systemctl daemon-reload
```

---

## Support

- **GitHub Issues**: https://github.com/YOUR_USERNAME/ProxyVault/issues
- **Documentation**: https://github.com/YOUR_USERNAME/ProxyVault
- **Discussions**: https://github.com/YOUR_USERNAME/ProxyVault/discussions

---

**Version**: 1.0.0  
**Last Updated**: January 2026
