# ProxyVault - Ubuntu VM Deployment Guide

## 🚀 Quick Installation

You're SSH'd into your Ubuntu VM. Let's install ProxyVault!

---

## Step 1: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/yaojeffrey/proxyVault.git
cd proxyVault
```

---

## Step 2: Run Installation Script

```bash
# Run the installer (requires sudo)
sudo bash scripts/install.sh
```

**What this does:**
- ✅ Updates system packages
- ✅ Installs Python, pip, dependencies
- ✅ Installs Hysteria 2 (latest)
- ✅ Installs Xray-core (for VLESS)
- ✅ Installs OpenVPN client
- ✅ Creates Python virtual environment
- ✅ Installs backend packages
- ✅ Creates systemd service
- ✅ Enables auto-start on boot
- ✅ Configures firewall (UFW)

**Installation time:** ~3-5 minutes

---

## Step 3: Change Default Password

**IMPORTANT: Change default credentials!**

```bash
# Edit configuration
sudo nano /opt/proxyvault/backend/.env
```

**Change these lines:**
```env
ADMIN_USERNAME=admin                    # Change this!
ADMIN_PASSWORD=admin123                 # Change this!
```

**Generate strong password:**
```bash
# Generate random password
openssl rand -base64 24
```

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

**Restart service:**
```bash
sudo systemctl restart proxyvault
```

---

## Step 4: Verify Installation

```bash
# Check if service is running
sudo systemctl status proxyvault

# Should show: "active (running)"

# Check logs
sudo journalctl -u proxyvault -n 50
```

**Expected output:**
```
● proxyvault.service - ProxyVault API Server
   Loaded: loaded
   Active: active (running)
   ...
   INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 5: Check Firewall

```bash
# View firewall status
sudo ufw status

# Should show:
# 8000/tcp    ALLOW    Anywhere
# 22/tcp      ALLOW    Anywhere (SSH)
```

---

## Step 6: Access via SSH Tunnel

**On your local machine (Windows):**

Open PowerShell:
```powershell
# Replace with your VM's IP address
ssh -L 8000:localhost:8000 ubuntu@YOUR_VM_IP
```

**Example:**
```powershell
ssh -L 8000:localhost:8000 ubuntu@203.0.113.45
```

**Keep this terminal open!**

---

## Step 7: Open Admin Panel

**On your local machine:**

Open browser to: http://localhost:8000/static/index.html

**Login with your new credentials!**

---

## 🎯 Quick Test Checklist

After accessing admin panel:

### Test 1: Dashboard
- [ ] Dashboard loads
- [ ] 4 service cards visible
- [ ] All show "Offline" initially

### Test 2: Monitoring
- [ ] Click "Monitoring" tab
- [ ] See real CPU/Memory/Disk stats
- [ ] Charts are updating
- [ ] Network interfaces listed

### Test 3: Hysteria Configuration
- [ ] Click "Hysteria" tab
- [ ] Check "Enable Port Hopping"
- [ ] Set range: 20000-30000
- [ ] Generate password
- [ ] Click "Save Configuration"

**Open firewall for Hysteria:**
```bash
sudo ufw allow 20000:30000/udp comment "Hysteria Port Hopping"
```

- [ ] Click "Start" button
- [ ] Dashboard shows green "Running"

### Test 4: VLESS Configuration
- [ ] Click "VLESS" tab
- [ ] Click "Generate UUID"
- [ ] Click "Generate New Keys"
- [ ] Click "Save Configuration"

**Open firewall for VLESS:**
```bash
sudo ufw allow 8443/tcp comment "VLESS"
```

- [ ] Click "Start" button
- [ ] Dashboard shows green "Running"

### Test 5: Logs
- [ ] Click "Logs" tab
- [ ] Select "ProxyVault API"
- [ ] See log entries
- [ ] Switch to "Hysteria"
- [ ] See Hysteria logs

---

## 🔧 Useful Commands

### Service Management
```bash
# Check status
sudo systemctl status proxyvault
sudo systemctl status hysteria-server
sudo systemctl status xray

# Start/Stop/Restart
sudo systemctl start proxyvault
sudo systemctl stop proxyvault
sudo systemctl restart proxyvault

# View logs
sudo journalctl -u proxyvault -f          # Follow logs
sudo journalctl -u hysteria-server -f     # Hysteria logs
sudo journalctl -u xray -f                # VLESS logs

# Check which ports are listening
sudo netstat -tlnp | grep -E "8000|20000|8443"
```

### Check Services
```bash
# Check if binaries are installed
which hysteria
which xray
which openvpn

# Check versions
hysteria version
xray version
```

### Firewall
```bash
# View all rules
sudo ufw status numbered

# Allow port
sudo ufw allow 8443/tcp

# Allow port range
sudo ufw allow 20000:30000/udp

# Delete rule
sudo ufw delete [number]
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check error
sudo systemctl status proxyvault

# View detailed logs
sudo journalctl -u proxyvault -n 100 --no-pager

# Common issue: Python dependencies
cd /opt/proxyvault/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Can't Access Admin Panel

```bash
# Check if service is listening
sudo netstat -tlnp | grep 8000

# Check firewall
sudo ufw status

# Test locally on VM
curl http://localhost:8000
```

### Hysteria Won't Start

```bash
# Check Hysteria logs
sudo journalctl -u hysteria-server -n 50

# Check config
sudo cat /etc/hysteria/config.yaml

# Test manually
sudo hysteria server --config /etc/hysteria/config.yaml
```

### Port Hopping Not Working

```bash
# Check firewall allows range
sudo ufw status | grep 20000

# If not, add it:
sudo ufw allow 20000:30000/udp

# Restart Hysteria
sudo systemctl restart hysteria-server
```

---

## 📊 What You Should See

### Working Installation:
```bash
$ sudo systemctl status proxyvault
● proxyvault.service - ProxyVault API Server
   Loaded: loaded (/etc/systemd/system/proxyvault.service)
   Active: active (running) since [timestamp]
   Main PID: [pid] (python)
   Memory: 45.2M
   CGroup: /system.slice/proxyvault.service
           └─[pid] /opt/proxyvault/venv/bin/python app.py
```

### Working Hysteria:
```bash
$ sudo systemctl status hysteria-server
● hysteria-server.service
   Loaded: loaded
   Active: active (running)
   Main PID: [pid] (hysteria)
```

### Open Ports:
```bash
$ sudo netstat -tlnp | grep -E "8000|36712"
tcp    0   0 0.0.0.0:8000    0.0.0.0:*    LISTEN    [pid]/python
udp    0   0 0.0.0.0:36712   0.0.0.0:*              [pid]/hysteria
```

---

## 🎉 Success Indicators

You'll know it's working when:

✅ `sudo systemctl status proxyvault` shows "active (running)"
✅ SSH tunnel connects without errors
✅ Admin panel loads at http://localhost:8000/static/index.html
✅ Can login with your credentials
✅ Monitoring shows real server stats
✅ Can configure and start Hysteria/VLESS
✅ Services show green "Running" on dashboard

---

## 🚀 Next Steps After Installation

1. **Configure Hysteria with port hopping**
2. **Configure VLESS + Reality**
3. **Test client connections**
4. **Setup OpenVPN (optional)**
5. **Enable traffic routing (optional)**

---

## 📝 Quick Copy-Paste Commands

```bash
# Complete installation sequence
git clone https://github.com/yaojeffrey/proxyVault.git
cd proxyVault
sudo bash scripts/install.sh

# Change password
sudo nano /opt/proxyvault/backend/.env
# (Change ADMIN_USERNAME and ADMIN_PASSWORD)
sudo systemctl restart proxyvault

# Check status
sudo systemctl status proxyvault

# Open firewall for Hysteria port hopping
sudo ufw allow 20000:30000/udp

# Open firewall for VLESS
sudo ufw allow 8443/tcp

# View logs
sudo journalctl -u proxyvault -f
```

---

**You're ready to install! Start with Step 1 and let me know if you hit any issues!** 🚀
