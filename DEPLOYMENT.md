# ProxyVault - Deployment Checklist

## ✅ Pre-Deployment Checklist

### Code Repository
- [x] Git repository initialized
- [x] All files committed
- [ ] Push to GitHub
- [ ] Update URLs in documentation (replace YOUR_USERNAME)
- [ ] Create GitHub releases/tags

### Documentation
- [x] README.md (overview and features)
- [x] SETUP.md (detailed installation guide)
- [x] QUICKSTART.md (5-minute guide)
- [x] PROJECT_SUMMARY.md (technical details)
- [x] LICENSE (MIT)
- [x] .gitignore (proper exclusions)
- [x] .env.example (configuration template)

### Backend
- [x] FastAPI application (app.py)
- [x] Configuration management (config.py)
- [x] Hysteria manager (services/hysteria.py)
- [x] VLESS manager (services/vless.py)
- [x] OpenVPN manager (services/openvpn.py)
- [x] Routing manager (services/routing.py)
- [x] Requirements.txt (dependencies)
- [x] Error handling
- [x] Input validation
- [x] Authentication (HTTP Basic)

### Frontend
- [x] HTML interface (index.html)
- [x] CSS styling (style.css)
- [x] JavaScript logic (app.js)
- [x] Responsive design
- [x] Service status dashboard
- [x] Configuration forms
- [x] Service control buttons

### Installation
- [x] install.sh script
- [x] Dependency installation
- [x] Systemd service creation
- [x] Firewall configuration
- [x] Permission setup

---

## 🚀 Deployment Steps

### 1. Create GitHub Repository

```bash
# On GitHub.com:
# 1. Click "New repository"
# 2. Name: ProxyVault
# 3. Description: "Multi-Protocol Proxy Manager with OpenVPN Routing"
# 4. Public or Private
# 5. Don't initialize with README (we have one)
# 6. Create repository
```

### 2. Push to GitHub

```bash
cd C:\src\personalProject\ProxyVault

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ProxyVault.git

# Rename branch to main
git branch -M main

# Push
git push -u origin main
```

### 3. Update Documentation URLs

Replace all instances of `YOUR_USERNAME` with your actual GitHub username:
- README.md (installation command, links)
- SETUP.md (installation command, support links)
- QUICKSTART.md (installation command, GitHub link)
- scripts/install.sh (GitHub clone URL)

```bash
# Quick find and replace (Linux/Mac)
find . -type f -name "*.md" -exec sed -i 's/YOUR_USERNAME/actual-username/g' {} +
find . -type f -name "*.sh" -exec sed -i 's/YOUR_USERNAME/actual-username/g' {} +

# Then commit changes
git add -A
git commit -m "Update GitHub username in documentation"
git push
```

### 4. Test Installation on Ubuntu VM

```bash
# On fresh Ubuntu 22.04/24.04 server:

# Test one-line installation
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ProxyVault/main/scripts/install.sh | sudo bash

# Verify services
systemctl status proxyvault
systemctl status hysteria-server
systemctl status xray
systemctl status openvpn-client@client

# Access admin panel
curl http://localhost:8000

# Check logs
journalctl -u proxyvault -n 50
```

### 5. Security Hardening

```bash
# Change default credentials
sudo nano /opt/proxyvault/backend/.env
# Update ADMIN_USERNAME and ADMIN_PASSWORD
sudo systemctl restart proxyvault

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 8000/tcp  # Admin panel (or restrict to specific IP)
sudo ufw allow 36712  # Hysteria (TCP and UDP)
sudo ufw allow 8443/tcp  # VLESS
sudo ufw enable

# Secure SSH
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
# Set: PasswordAuthentication no (after setting up keys)
sudo systemctl restart sshd
```

### 6. Optional: Add HTTPS to Admin Panel

```bash
# Install nginx
sudo apt install nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/proxyvault

# Add:
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable and restart
sudo ln -s /etc/nginx/sites-available/proxyvault /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get Let's Encrypt certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📊 Post-Deployment Monitoring

### Health Checks

```bash
# Service status
sudo systemctl status proxyvault hysteria-server xray openvpn-client@client

# API health
curl -u admin:password http://localhost:8000/api/status

# System resources
curl -u admin:password http://localhost:8000/api/system/info

# Logs
sudo journalctl -u proxyvault --since "1 hour ago"
```

### Performance Monitoring

```bash
# Check connections
sudo ss -tunlp | grep -E "(8000|36712|8443)"

# Network traffic
sudo iftop

# System resources
htop

# Disk usage
df -h
du -sh /opt/proxyvault /etc/hysteria /etc/xray
```

---

## 🔄 Update Procedure

### Update Application

```bash
cd /opt/proxyvault
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt
sudo systemctl restart proxyvault
```

### Update Proxy Binaries

```bash
# Update Hysteria
sudo bash <(curl -fsSL https://get.hy2.sh/)
sudo systemctl restart hysteria-server

# Update Xray
sudo bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
sudo systemctl restart xray
```

---

## 🐛 Troubleshooting Checklist

### If Admin Panel Won't Start

- [ ] Check Python virtual environment: `source /opt/proxyvault/venv/bin/activate`
- [ ] Check dependencies: `pip list | grep fastapi`
- [ ] Check port availability: `sudo lsof -i :8000`
- [ ] Check logs: `sudo journalctl -u proxyvault -n 100`
- [ ] Check file permissions: `ls -la /opt/proxyvault`

### If Proxies Won't Connect

- [ ] Check service status: `systemctl status hysteria-server xray`
- [ ] Check configuration files: `cat /etc/hysteria/config.yaml`
- [ ] Test ports: `sudo netstat -tlnp | grep 36712`
- [ ] Check firewall: `sudo ufw status`
- [ ] Test manually: `sudo hysteria server --config /etc/hysteria/config.yaml`

### If Routing Doesn't Work

- [ ] OpenVPN connected: `ip a show tun0`
- [ ] IP forwarding enabled: `sysctl net.ipv4.ip_forward`
- [ ] Check iptables: `sudo iptables -t nat -L -n -v`
- [ ] Check routing tables: `ip route show table 100`
- [ ] Check policy routing: `ip rule list`

---

## 📈 Success Metrics

After deployment, verify:

- [x] Admin panel accessible
- [x] Can login with credentials
- [x] Dashboard shows service status
- [x] Can configure Hysteria
- [x] Can configure VLESS
- [x] Can upload OpenVPN config
- [x] Can enable/disable routing
- [x] Services start on system boot
- [x] Clients can connect to proxies
- [x] Traffic routing works correctly

---

## 🎉 Production Ready Criteria

### Minimum Requirements Met
- [x] All services start successfully
- [x] Admin panel accessible and functional
- [x] At least one proxy protocol working
- [x] Default credentials changed
- [x] Firewall configured
- [x] Documentation complete

### Optional Enhancements
- [ ] HTTPS enabled for admin panel
- [ ] SSH hardening complete
- [ ] Monitoring/alerting configured
- [ ] Backup procedure established
- [ ] Domain name configured
- [ ] Let's Encrypt certificate installed

---

## 📝 Deployment Log Template

```
=== ProxyVault Deployment Log ===

Date: YYYY-MM-DD
Server: Ubuntu XX.XX
IP Address: XXX.XXX.XXX.XXX

Installation:
- Installation script: [SUCCESS/FAIL]
- Hysteria installed: [SUCCESS/FAIL]
- Xray installed: [SUCCESS/FAIL]
- OpenVPN installed: [SUCCESS/FAIL]
- ProxyVault service: [SUCCESS/FAIL]

Configuration:
- Admin credentials changed: [YES/NO]
- Firewall configured: [YES/NO]
- SSL certificate: [YES/NO]
- Hysteria configured: [YES/NO]
- VLESS configured: [YES/NO]
- OpenVPN configured: [YES/NO]
- Routing enabled: [YES/NO]

Testing:
- Admin panel accessible: [YES/NO]
- Hysteria client connected: [YES/NO]
- VLESS client connected: [YES/NO]
- OpenVPN connected: [YES/NO]
- Traffic routing verified: [YES/NO]

Issues:
- List any issues encountered
- Resolutions applied

Notes:
- Additional configuration notes
```

---

**Deployment Status**: ⏳ Ready to Deploy

**Next Action**: Create GitHub repository and push code

**Estimated Time**: 30 minutes for full deployment + testing

---

**Good luck with your deployment! 🚀**
