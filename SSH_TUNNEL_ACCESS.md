# SSH Tunnel Access Guide

## 🔐 Secure Remote Access via SSH Tunnel

**Why SSH Tunnel?**
- ✅ Zero public exposure (admin panel never touches internet)
- ✅ Encrypted connection (SSH encryption)
- ✅ No SSL certificate needed
- ✅ No additional software required
- ✅ Uses existing SSH authentication
- ✅ Simplest secure solution

---

## 🚀 Quick Setup

### On Ubuntu Server (One-Time Setup)

#### 1. Ensure ProxyVault is Running
```bash
sudo systemctl status proxyvault
# Should show "active (running)"
```

#### 2. Ensure SSH is Accessible
```bash
# Check SSH is running
sudo systemctl status ssh

# Check SSH port (usually 22)
sudo netstat -tlnp | grep ssh

# Make sure firewall allows SSH
sudo ufw allow 22/tcp
```

#### 3. Block Public Access to Admin Panel
```bash
# ProxyVault should ONLY listen on localhost
# Verify it's not publicly accessible
sudo netstat -tlnp | grep 8000

# Should show: 127.0.0.1:8000 or 0.0.0.0:8000

# If you want extra security, firewall block it:
sudo ufw deny 8000/tcp
```

---

## 💻 From Your Local Computer

### Windows (PowerShell or CMD)

```powershell
# Create SSH tunnel
ssh -L 8000:localhost:8000 username@your-server-ip

# Example:
ssh -L 8000:localhost:8000 ubuntu@203.0.113.45
```

**Then in browser:**
```
http://localhost:8000/static/index.html
```

### macOS / Linux (Terminal)

```bash
# Create SSH tunnel
ssh -L 8000:localhost:8000 username@your-server-ip

# Example:
ssh -L 8000:localhost:8000 ubuntu@203.0.113.45
```

**Then in browser:**
```
http://localhost:8000/static/index.html
```

---

## 📋 Step-by-Step Usage

### Every Time You Want to Access ProxyVault:

**Step 1:** Open terminal/PowerShell

**Step 2:** Connect with SSH tunnel
```bash
ssh -L 8000:localhost:8000 user@server-ip
```

**Step 3:** Keep terminal window open (don't close it!)

**Step 4:** Open browser to `http://localhost:8000/static/index.html`

**Step 5:** Login with admin credentials

**Step 6:** Use ProxyVault normally

**Step 7:** When done, close browser and press `Ctrl+C` in terminal to disconnect

---

## 🔧 Advanced Options

### Run in Background (Linux/Mac)

```bash
# Run SSH tunnel in background
ssh -fN -L 8000:localhost:8000 user@server-ip

# Check if running
ps aux | grep ssh

# Kill when done
pkill -f "8000:localhost:8000"
```

### Multiple Ports (If Needed)

```bash
# Tunnel multiple services at once
ssh -L 8000:localhost:8000 \
    -L 36712:localhost:36712 \
    -L 8443:localhost:8443 \
    user@server-ip
```

### Custom SSH Port

```bash
# If SSH is on non-standard port (e.g., 2222)
ssh -p 2222 -L 8000:localhost:8000 user@server-ip
```

### Use SSH Config File

**Create/edit `~/.ssh/config`:**
```
Host proxyvault
    HostName your-server-ip
    User ubuntu
    Port 22
    LocalForward 8000 localhost:8000
```

**Then simply:**
```bash
ssh proxyvault
```

---

## 🔑 SSH Key Authentication (Recommended)

### Setup SSH Keys (More Secure Than Password)

#### On Your Local Computer:

**Generate SSH key (if you don't have one):**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

**Copy public key to server:**
```bash
ssh-copy-id user@server-ip
```

#### On Ubuntu Server:

**Disable password authentication (optional but recommended):**
```bash
sudo nano /etc/ssh/sshd_config
```

**Change these lines:**
```
PasswordAuthentication no
PubkeyAuthentication yes
```

**Restart SSH:**
```bash
sudo systemctl restart ssh
```

**Now SSH login won't ask for password!**

---

## 🌐 Access from Multiple Locations

### From Home
```bash
ssh -L 8000:localhost:8000 user@server-ip
# Access: http://localhost:8000
```

### From Office
```bash
ssh -L 8000:localhost:8000 user@server-ip
# Access: http://localhost:8000
```

### From Laptop on Coffee Shop WiFi
```bash
ssh -L 8000:localhost:8000 user@server-ip
# Access: http://localhost:8000
```

**Always secure - even on untrusted networks!** ✅

---

## 🐛 Troubleshooting

### "Connection refused"
**Problem:** Can't connect to SSH
**Solution:**
```bash
# Check if SSH is running on server
sudo systemctl status ssh

# Check firewall
sudo ufw status

# Allow SSH if blocked
sudo ufw allow 22/tcp
```

### "Port 8000 already in use"
**Problem:** Another program is using port 8000 locally
**Solution:**
```bash
# Use different local port
ssh -L 8001:localhost:8000 user@server-ip
# Then access: http://localhost:8001
```

### "Permission denied"
**Problem:** Wrong username or SSH keys not setup
**Solution:**
```bash
# Check username
ssh user@server-ip whoami

# Check SSH key
ssh -v user@server-ip  # Verbose mode shows auth details
```

### "Cannot access localhost:8000"
**Problem:** ProxyVault not running on server
**Solution:**
```bash
# On server, check service
sudo systemctl status proxyvault
sudo systemctl start proxyvault
```

### Tunnel Disconnects Frequently
**Problem:** Network instability or timeout
**Solution:**
```bash
# Add keep-alive options
ssh -o ServerAliveInterval=60 \
    -o ServerAliveCountMax=3 \
    -L 8000:localhost:8000 user@server-ip
```

---

## 📱 Mobile Access

### iOS (Using Termius App)
1. Install Termius from App Store
2. Add server connection
3. Enable port forwarding: 8000 → localhost:8000
4. Connect
5. Open Safari to `http://localhost:8000`

### Android (Using JuiceSSH)
1. Install JuiceSSH from Play Store
2. Add connection
3. Configure port forward: 8000 → localhost:8000
4. Connect
5. Open Chrome to `http://localhost:8000`

---

## 🔐 Security Benefits

### What SSH Tunnel Protects Against:

✅ **Man-in-the-middle attacks** - All traffic encrypted
✅ **Credential sniffing** - SSH encryption
✅ **Port scanning** - Admin panel not exposed
✅ **Brute force attacks** - SSH key authentication
✅ **DDoS attacks** - No public web service
✅ **Zero-day exploits** - No attack surface

### Attack Surface:

**Without SSH Tunnel:**
```
Internet → [Port 8000 Open] → ProxyVault
          ↑ Anyone can try to attack this
```

**With SSH Tunnel:**
```
Internet → [Only SSH Port 22] → Server
           ↑ Only SSH access (key auth)
           
You → [SSH Tunnel] → localhost:8000 → ProxyVault
      ↑ Encrypted, no public exposure
```

---

## 📊 Comparison with Other Methods

| Method | Security | Complexity | Cost |
|--------|----------|------------|------|
| **SSH Tunnel** | ✅✅✅ Excellent | ⭐ Very Simple | Free |
| Public + HTTPS | ✅✅ Good | ⭐⭐ Medium | Free |
| Public + HTTP | ❌ Unsafe | ⭐ Simple | Free |
| Tailscale VPN | ✅✅✅ Excellent | ⭐ Simple | Free |
| WireGuard VPN | ✅✅✅ Excellent | ⭐⭐⭐ Complex | Free |

---

## 🎯 Best Practices

### ✅ Do This:
- Use SSH key authentication (not passwords)
- Keep SSH tunnel open while using ProxyVault
- Close tunnel when done
- Use strong SSH passphrase
- Update SSH regularly: `sudo apt update && sudo apt upgrade openssh-server`

### ❌ Don't Do This:
- Don't expose port 8000 to internet
- Don't use weak SSH passwords
- Don't share SSH keys
- Don't leave tunnel running when not in use (optional)

---

## 🚀 Quick Reference Card

**Connect:**
```bash
ssh -L 8000:localhost:8000 user@server-ip
```

**Access:**
```
http://localhost:8000/static/index.html
```

**Disconnect:**
```
Ctrl+C in terminal
```

**Background Mode:**
```bash
ssh -fN -L 8000:localhost:8000 user@server-ip
```

**Kill Background:**
```bash
pkill -f "8000:localhost:8000"
```

---

## 📝 Example Session

```bash
# Start tunnel
$ ssh -L 8000:localhost:8000 ubuntu@203.0.113.45
ubuntu@server:~$ 

# Keep this terminal open

# In another terminal or browser:
# Open: http://localhost:8000/static/index.html
# Use ProxyVault normally

# When done, go back to SSH terminal:
ubuntu@server:~$ exit
# Or press Ctrl+C

# Tunnel closed, ProxyVault no longer accessible
```

---

## ✅ Setup Complete

**Your secure access method:**
1. SSH tunnel to server
2. Access via localhost
3. Zero public exposure
4. Maximum security

**No additional setup needed on server!**
ProxyVault already listens on all interfaces, SSH tunnel redirects traffic securely.

---

**Security Status:** 🔒 **SECURE**  
**Public Exposure:** ❌ **NONE**  
**Encryption:** ✅ **SSH (Yes)**  
**Authentication:** ✅ **SSH Keys**  
**Ease of Use:** ⭐⭐⭐⭐⭐

---

**You're all set!** 🎉
