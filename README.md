# 🔐 ProxyVault

**Multi-Protocol Proxy Manager with OpenVPN Routing**

A web-based admin panel to configure and manage proxy protocols (Hysteria, VLESS+Reality) on Ubuntu VMs with intelligent traffic routing through OpenVPN.

---

## 🌟 Features

- ✅ **Hysteria 2** - Latest high-performance proxy protocol
- ✅ **VLESS + Reality** - Anti-censorship proxy with TLS camouflage
- ✅ **OpenVPN Integration** - Route all proxy traffic through OpenVPN
- ✅ **Web Admin UI** - Easy configuration through modern web interface
- ✅ **Traffic Routing** - Automatic iptables configuration for transparent routing
- ✅ **Service Management** - Start/stop/restart services with one click
- ✅ **Real-time Monitoring** - System resources, bandwidth, connections, logs
- ✅ **Interactive Charts** - CPU, memory, network traffic visualization
- ✅ **Logs Viewer** - Live service logs with auto-refresh
- ✅ **Quick Setup** - One-line installation script for Ubuntu

---

## 🏗️ Architecture

```
Internet
   ↓
[Hysteria / VLESS] ← Inbound proxy protocols
   ↓
[Traffic Router] ← iptables rules
   ↓
[OpenVPN Client] ← Outbound through VPN
   ↓
Internet
```

**Traffic Flow:**
- Proxy traffic (Hysteria/VLESS) → OpenVPN → Internet
- Direct SSH/Management traffic → Direct (no OpenVPN)

---

## 🚀 Quick Start

### Prerequisites

- Ubuntu 22.04 or 24.04 LTS
- Root or sudo access
- Minimum 1GB RAM, 10GB disk
- Public IP address

### One-Line Installation

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ProxyVault/main/scripts/install.sh | sudo bash
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ProxyVault.git
cd ProxyVault

# Run installation script
sudo bash scripts/install.sh

# Access admin panel
# http://YOUR_SERVER_IP:8000
```

---

## 📖 Usage

### 1. Access Admin Panel

```
http://YOUR_SERVER_IP:8000
Default credentials: admin / admin123
```

### 2. Monitor System (NEW!)

- Navigate to **Monitoring** tab
- View real-time CPU, memory, disk usage
- Track network bandwidth with interactive charts
- Monitor active connections per protocol
- View service logs with auto-refresh

### 3. Configure Hysteria

- Navigate to **Hysteria** tab
- Set port, password, and obfuscation settings
- Click **Save & Start**

### 4. Configure VLESS + Reality

- Navigate to **VLESS** tab
- Generate UUID or use existing
- Set target domain for Reality camouflage
- Configure port and keys
- Click **Save & Start**

### 5. Setup OpenVPN (Optional)

- Navigate to **OpenVPN** tab
- Upload your `.ovpn` configuration file
- Enter credentials if required
- Click **Connect**

### 6. Enable Traffic Routing

- Check **"Route proxy traffic through OpenVPN"**
- System will automatically configure iptables rules
- Verify routing is active in Dashboard

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
API_PORT=8000

# Services
HYSTERIA_PORT=36712
VLESS_PORT=8443

# OpenVPN
OPENVPN_CONFIG_PATH=/etc/openvpn/client.conf
```

### Manual Service Control

```bash
# Hysteria
sudo systemctl start hysteria
sudo systemctl status hysteria

# VLESS (Xray)
sudo systemctl start xray
sudo systemctl status xray

# OpenVPN
sudo systemctl start openvpn-client@client
sudo systemctl status openvpn-client@client
```

---

## 📁 Project Structure

```
ProxyVault/
├── backend/              # FastAPI backend
│   ├── app.py           # Main API server
│   ├── config.py        # Configuration management
│   ├── services/        # Service controllers
│   │   ├── hysteria.py
│   │   ├── vless.py
│   │   └── openvpn.py
│   └── routes/          # API endpoints
├── frontend/            # Vue.js admin UI
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   └── App.vue
│   └── public/
├── services/            # Service configurations
│   ├── hysteria/
│   ├── vless/
│   └── openvpn/
├── scripts/             # Installation scripts
│   ├── install.sh       # Main installer
│   └── setup-routing.sh # iptables configuration
└── docker/              # Docker deployment (optional)
    └── docker-compose.yml
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+ with FastAPI
- **Frontend**: Vue.js 3 with Vite
- **Database**: SQLite (embedded)
- **Proxy Protocols**:
  - Hysteria 2 (official binary)
  - Xray-core (for VLESS+Reality)
  - OpenVPN (system package)

---

## 🔒 Security Notes

1. **Change default credentials** immediately after installation
2. **Use HTTPS** for admin panel in production (add reverse proxy)
3. **Firewall**: Only expose necessary ports (Hysteria, VLESS, admin panel)
4. **OpenVPN credentials**: Stored encrypted on disk
5. **Regular updates**: Keep all components updated

---

## 📊 Monitoring

Dashboard shows:
- Service status (running/stopped)
- Active connections
- Traffic statistics
- OpenVPN connection status
- System resource usage

---

## 🐛 Troubleshooting

### Admin panel not accessible
```bash
# Check if backend is running
sudo systemctl status proxyvault

# Check logs
sudo journalctl -u proxyvault -f
```

### Hysteria/VLESS not starting
```bash
# Check configuration
cat /etc/hysteria/config.yaml
cat /etc/xray/config.json

# Test manually
hysteria server --config /etc/hysteria/config.yaml
```

### OpenVPN not connecting
```bash
# Check OpenVPN logs
sudo journalctl -u openvpn-client@client -f

# Test connection
sudo openvpn --config /etc/openvpn/client.conf
```

### Traffic not routing through OpenVPN
```bash
# Check iptables rules
sudo iptables -t nat -L -n -v

# Verify OpenVPN interface
ip a show tun0
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🆘 Support

- **Issues**: https://github.com/YOUR_USERNAME/ProxyVault/issues
- **Discussions**: https://github.com/YOUR_USERNAME/ProxyVault/discussions

---

## 🗺️ Roadmap

- [ ] Additional protocols (Shadowsocks, Trojan)
- [ ] Multi-user management
- [ ] Traffic statistics and analytics
- [ ] Automatic certificate renewal (Reality)
- [ ] Backup/restore configurations
- [ ] Mobile-friendly UI
- [ ] Docker deployment option
- [ ] WireGuard support (alternative to OpenVPN)

---

**Created by:** Your Name  
**Version:** 1.0.0  
**Last Updated:** January 2026
