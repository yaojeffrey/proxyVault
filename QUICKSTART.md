# ProxyVault - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install (On Ubuntu Server)

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ProxyVault/main/scripts/install.sh | sudo bash
```

Wait for installation to complete (2-3 minutes).

### Step 2: Access Admin Panel

Open browser:
```
http://YOUR_SERVER_IP:8000
```

Login:
- Username: `admin`
- Password: `admin123`

⚠️ **Change password immediately!**

### Step 3: Change Default Password

Edit configuration:
```bash
sudo nano /opt/proxyvault/backend/.env
```

Change:
```env
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_strong_password
```

Restart:
```bash
sudo systemctl restart proxyvault
```

### Step 4: Configure Your First Proxy

#### Option A: Hysteria 2 (Fastest)

1. Go to **Hysteria** tab
2. Click **Generate** button for password
3. Click **Save Configuration**
4. Click **Start**
5. ✅ Green status = Running!

**Client config** (Hysteria client):
```yaml
server: YOUR_SERVER_IP:36712
auth: YOUR_GENERATED_PASSWORD
bandwidth:
  up: 100 mbps
  down: 100 mbps
socks5:
  listen: 127.0.0.1:1080
```

#### Option B: VLESS + Reality (Most Stealthy)

1. Go to **VLESS** tab
2. Click **Generate UUID**
3. Click **Generate New Keys**
4. Click **Save Configuration**
5. Click **Start**
6. ✅ Green status = Running!

**Client config** (v2rayN/Nekoray):
- Protocol: VLESS
- Address: YOUR_SERVER_IP
- Port: 8443
- UUID: [from web UI]
- Flow: xtls-rprx-vision
- Security: reality
- SNI: www.microsoft.com
- Public Key: [from web UI]

### Step 5: (Optional) Add OpenVPN Routing

If you have an OpenVPN provider:

1. Download your .ovpn file from provider
2. Go to **OpenVPN** tab
3. Click **Choose File** and select .ovpn
4. Enter username/password if required
5. Click **Save & Connect**
6. Wait for green status
7. Go to **Routing** tab
8. Click **Enable Routing**
9. ✅ All proxy traffic now goes through OpenVPN!

---

## 🎯 What You Get

✅ **Hysteria 2**: Ultra-fast proxy with UDP optimization  
✅ **VLESS + Reality**: Stealth proxy that looks like regular HTTPS  
✅ **OpenVPN Routing**: Chain proxies through VPN for extra layer  
✅ **Web UI**: Easy management, no command line needed  
✅ **Auto-start**: Services start automatically on boot  

---

## 🔒 Security Checklist

After installation, do these immediately:

- [ ] Change default admin password
- [ ] Configure firewall (ufw)
- [ ] Use strong proxy passwords
- [ ] Restrict admin panel access to your IP only
- [ ] Disable root SSH login
- [ ] Enable automatic security updates

---

## 📱 Client Downloads

### Hysteria Clients
- **Windows/Mac/Linux**: https://github.com/apernet/hysteria/releases
- **Android**: https://github.com/SagerNet/SagerNet
- **iOS**: Shadowrocket, Surge

### VLESS Clients
- **Windows**: v2rayN https://github.com/2dust/v2rayN/releases
- **Android**: v2rayNG, Nekoray
- **iOS**: Shadowrocket, Quantumult X
- **Mac/Linux**: Qv2ray, Nekoray

---

## 🆘 Common Issues

### Can't access admin panel
```bash
# Check if service is running
sudo systemctl status proxyvault

# Check firewall
sudo ufw allow 8000/tcp

# View logs
sudo journalctl -u proxyvault -f
```

### Proxy not connecting
```bash
# Check service status
sudo systemctl status hysteria-server  # or xray

# View logs
sudo journalctl -u hysteria-server -f  # or xray -f

# Restart service
sudo systemctl restart hysteria-server  # or xray
```

### OpenVPN not connecting
```bash
# Check configuration
sudo cat /etc/openvpn/client/client.conf

# Test manually
sudo openvpn --config /etc/openvpn/client/client.conf

# View logs
sudo journalctl -u openvpn-client@client -f
```

---

## 📚 Full Documentation

- **Detailed Setup**: See [SETUP.md](SETUP.md)
- **Complete Guide**: See [README.md](README.md)
- **Project Info**: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 💡 Pro Tips

1. **Performance**: Enable BBR congestion control for better speed
2. **Security**: Use SSH tunnel for admin panel access
3. **Reliability**: Set up monitoring and auto-restart
4. **Firewall**: Only open ports you actually use
5. **Backup**: Save your configurations regularly

---

## 🎉 You're Done!

Your proxy server is now running and ready to use!

**Need help?** Open an issue on GitHub: `YOUR_USERNAME/ProxyVault/issues`

---

**Quick Links:**
- Dashboard: http://YOUR_SERVER_IP:8000
- GitHub: https://github.com/YOUR_USERNAME/ProxyVault
- Hysteria Docs: https://v2.hysteria.network/
- Xray Docs: https://xtls.github.io/

**Happy proxying! 🚀**
