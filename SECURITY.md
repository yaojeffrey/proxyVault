# Secure Public Deployment Guide

## 🔒 Making ProxyVault Public-Safe

### Option 1: Nginx + Let's Encrypt (RECOMMENDED)

#### Step 1: Install Nginx
```bash
sudo apt install nginx certbot python3-certbot-nginx
```

#### Step 2: Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/proxyvault
```

**Add this configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration (will be added by certbot)
    # ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate Limiting (10 requests per minute per IP)
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;
    limit_req zone=api_limit burst=20 nodelay;
    
    # IP Whitelist (Optional - Restrict to your IPs)
    # allow 1.2.3.4;       # Your home IP
    # allow 5.6.7.8;       # Your office IP
    # deny all;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

#### Step 3: Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/proxyvault /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 4: Get SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

#### Step 5: Change Default Password
```bash
sudo nano /opt/proxyvault/backend/.env
```
Change:
```env
ADMIN_USERNAME=your_unique_username
ADMIN_PASSWORD=your_very_strong_password_here_32_chars_min
```

Restart:
```bash
sudo systemctl restart proxyvault
```

---

### Option 2: IP Whitelist (Restrictive)

**Block everyone except your IPs:**

```bash
# In firewall
sudo ufw deny 8000/tcp
sudo ufw allow from YOUR_HOME_IP to any port 8000
sudo ufw allow from YOUR_OFFICE_IP to any port 8000
```

**Or in nginx:**
```nginx
location / {
    allow 1.2.3.4;      # Your IP
    allow 5.6.7.8;      # Another trusted IP
    deny all;           # Block everyone else
    
    proxy_pass http://localhost:8000;
}
```

---

### Option 3: VPN/Tailscale Only

**Don't expose to public internet at all:**

1. **Install Tailscale** (zero-config VPN)
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

2. **Access via Tailscale IP**
```
http://100.x.x.x:8000
```

3. **Firewall blocks public**
```bash
sudo ufw deny 8000/tcp  # Block public
# Access only via Tailscale network
```

---

### Option 4: SSH Tunnel (Most Secure)

**Never expose admin panel publicly:**

```bash
# From your local machine
ssh -L 8000:localhost:8000 user@your-server.com

# Then access locally
http://localhost:8000
```

**Advantages:**
- ✅ Zero public exposure
- ✅ Uses SSH authentication
- ✅ Encrypted tunnel
- ✅ No SSL certificate needed

---

## 🔐 Enhanced Security Checklist

### Before Public Exposure:

- [ ] **HTTPS enabled** (Let's Encrypt)
- [ ] **Strong password** (32+ characters, random)
- [ ] **Change default username** (not "admin")
- [ ] **Rate limiting** (nginx or fail2ban)
- [ ] **IP whitelist** (if possible)
- [ ] **Security headers** (HSTS, CSP, X-Frame-Options)
- [ ] **Firewall configured** (only necessary ports)
- [ ] **Disable root SSH** (`PermitRootLogin no`)
- [ ] **SSH key auth only** (disable password auth)
- [ ] **Automatic updates** enabled
- [ ] **Monitoring/alerts** configured
- [ ] **Backup credentials** stored safely

---

## 🚨 Additional Security Measures

### 1. Add Rate Limiting to Backend

**Install dependency:**
```bash
pip install slowapi
```

**Add to app.py:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@app.post("/api/hysteria/config")
@limiter.limit("10/minute")
async def update_hysteria_config(...):
    ...
```

### 2. Add fail2ban Protection

**Install fail2ban:**
```bash
sudo apt install fail2ban
```

**Create filter:**
```bash
sudo nano /etc/fail2ban/filter.d/proxyvault.conf
```

```ini
[Definition]
failregex = .*401 Unauthorized.*<HOST>
ignoreregex =
```

**Configure jail:**
```bash
sudo nano /etc/fail2ban/jail.local
```

```ini
[proxyvault]
enabled = true
port = 8000
filter = proxyvault
logpath = /var/log/proxyvault/access.log
maxretry = 3
bantime = 3600
findtime = 600
```

### 3. Add JWT Authentication (Advanced)

Replace HTTP Basic Auth with JWT tokens:
- Login endpoint returns JWT
- JWT expires after X hours
- Refresh tokens for renewal
- More secure than Basic Auth

---

## 📊 Security Comparison

| Method | Security | Ease | Cost |
|--------|----------|------|------|
| **HTTP Basic Auth Only** | ⚠️ Low | Easy | Free |
| **+ HTTPS (Let's Encrypt)** | ✅ Good | Easy | Free |
| **+ IP Whitelist** | ✅✅ Better | Medium | Free |
| **+ Rate Limiting** | ✅✅ Better | Medium | Free |
| **VPN Only (Tailscale)** | ✅✅✅ Best | Easy | Free |
| **SSH Tunnel Only** | ✅✅✅ Best | Easy | Free |
| **+ JWT + 2FA** | ✅✅✅✅ Enterprise | Hard | Free |

---

## 🎯 Recommendations by Use Case

### Personal Use (You Only)
**→ SSH Tunnel or Tailscale**
- No public exposure
- Simplest and most secure

### Small Team (2-5 People)
**→ Nginx + HTTPS + IP Whitelist**
- Each person's IP allowed
- SSL encryption
- Rate limiting

### Public Facing (Not Recommended)
**→ Nginx + HTTPS + Strong Auth + Rate Limiting + Fail2ban**
- All security layers
- Monitor logs constantly
- Consider JWT + 2FA

---

## ⚠️ Current State: NOT PUBLIC-SAFE

**Your ProxyVault right now:**
- ❌ HTTP only (plaintext)
- ❌ Default credentials
- ❌ No rate limiting
- ❌ No brute-force protection

**Do NOT expose to internet until:**
1. HTTPS enabled (Let's Encrypt)
2. Strong password set
3. Rate limiting added
4. Firewall configured

---

## 🔧 Quick Security Setup (5 Minutes)

**Minimum viable security:**

```bash
# 1. Change password
sudo nano /opt/proxyvault/backend/.env
# Set strong password: generate with: openssl rand -base64 32

# 2. Setup nginx with HTTPS
sudo apt install nginx certbot python3-certbot-nginx
# (Follow Option 1 steps above)

# 3. Firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Block direct access
sudo ufw enable

# 4. Restart
sudo systemctl restart proxyvault nginx
```

---

**Bottom Line:**
- ✅ **Local network**: Current auth is fine
- ⚠️ **Public internet**: MUST add HTTPS + strong password minimum
- ✅ **Best option**: Use SSH tunnel or Tailscale (no public exposure)

Would you like me to:
1. Add enhanced authentication (JWT, rate limiting)?
2. Create nginx + SSL configuration files?
3. Add IP whitelist functionality?
4. Set up Tailscale instructions?
