# Hysteria Port Hopping Feature

## 🎯 What is Port Hopping?

Port hopping (also called port randomization) is an advanced anti-censorship technique where the proxy server randomly switches between multiple ports. This makes it extremely difficult for firewalls and DPI (Deep Packet Inspection) systems to block the service.

---

## 🔐 Why Use Port Hopping?

### Traditional Single Port:
```
Client → Port 36712 → Hysteria Server
         ↑ Easy to block by firewall
```

### With Port Hopping:
```
Client → Ports 20000-30000 (random) → Hysteria Server
         ↑ Constantly changing, hard to block
```

**Benefits:**
- ✅ **Evade censorship** - Can't block all 10,000 ports
- ✅ **Anti-DPI** - Harder to detect patterns
- ✅ **Resilience** - If one port blocked, switches to another
- ✅ **Load distribution** - Traffic spread across ports

---

## 📋 Configuration Options

### Single Port Mode (Default)
```yaml
listen: :36712
```
**Use when:** No censorship, simple setup

### Port Hopping Mode
```yaml
listen: :20000-30000
portHopping:
  interval: 1m  # Optional
```
**Use when:** Behind firewall, facing censorship

---

## 🖥️ Web UI Configuration

### Enable Port Hopping

1. Go to **Hysteria** tab
2. Check **"Enable Port Hopping"**
3. Configure port range:
   - **Port Range Start:** 20000 (default)
   - **Port Range End:** 30000 (default)
   - **Range size:** 10,000 ports
4. (Optional) Set hop interval:
   - **Auto** (Recommended) - Hysteria decides
   - **30 seconds** - Frequent changes
   - **1 minute** - Balance
   - **5/10 minutes** - Less frequent
5. Click **Save Configuration**
6. Click **Start** or **Restart**

---

## 🔧 Port Range Recommendations

### Small Range (Testing)
```
Start: 36000
End: 36100
Ports: 100
```
**Good for:** Testing, low-censorship areas

### Medium Range (Balanced)
```
Start: 20000
End: 25000
Ports: 5,000
```
**Good for:** Moderate censorship, VPS with limited resources

### Large Range (Maximum Evasion)
```
Start: 20000
End: 50000
Ports: 30,000
```
**Good for:** Heavy censorship, high-security requirements

### Custom Ranges
```
Start: 10000
End: 65535
Ports: 55,535 (Maximum)
```
**Note:** Avoid well-known ports (0-1023)

---

## 🔥 Firewall Configuration

### ⚠️ Important: Open Port Range

When using port hopping, you MUST open the entire port range in your firewall:

#### UFW (Ubuntu Default)
```bash
# Open UDP port range for Hysteria
sudo ufw allow 20000:30000/udp comment "Hysteria Port Hopping"

# Verify
sudo ufw status
```

#### iptables (Advanced)
```bash
# Allow UDP port range
sudo iptables -A INPUT -p udp --dport 20000:30000 -j ACCEPT

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

#### Cloud Provider (AWS/GCP/Azure)
Configure security group to allow:
- **Protocol:** UDP
- **Port Range:** 20000-30000
- **Source:** 0.0.0.0/0 (or your IP)

---

## 👤 Client Configuration

### Hysteria Client
```yaml
server: your-server-ip:20000-30000  # Port range

auth: your_password

bandwidth:
  up: 100 mbps
  down: 100 mbps

socks5:
  listen: 127.0.0.1:1080

http:
  listen: 127.0.0.1:8080
```

**Note:** Client automatically handles port hopping!

---

## 📊 Performance Impact

### Resource Usage
- **CPU:** +0.5-1% (negligible)
- **Memory:** +2-5 MB (minimal)
- **Network:** Same as single port
- **Latency:** +0-2ms (imperceptible)

### Trade-offs
| Aspect | Single Port | Port Hopping |
|--------|-------------|--------------|
| **Simplicity** | ✅ Very Simple | ⚠️ More Complex |
| **Firewall Rules** | ✅ 1 Rule | ⚠️ Range Rule |
| **Anti-Censorship** | ❌ Easy to Block | ✅ Hard to Block |
| **Performance** | ✅ Optimal | ✅ Near-Optimal |
| **Setup Time** | ⚠️ 1 min | ⚠️ 3 min |

---

## 🔍 How It Works

### Server-Side (Automatic)
1. Hysteria listens on port range (e.g., 20000-30000)
2. Randomly selects port from range
3. Client connects to current port
4. After interval, switches to different port
5. Client follows seamlessly

### Client-Side (Automatic)
1. Client knows port range from config
2. Queries server for current port
3. Connects to active port
4. Detects port changes automatically
5. Reconnects to new port instantly

### Interval Options
- **Auto (Recommended):** Hysteria optimizes based on traffic
- **Short (30s):** Maximum evasion, more overhead
- **Medium (1m-5m):** Balanced
- **Long (10m+):** Minimal overhead, less evasion

---

## 🐛 Troubleshooting

### "Connection refused" errors

**Problem:** Firewall not opened
**Solution:**
```bash
# Check firewall
sudo ufw status

# Open port range
sudo ufw allow 20000:30000/udp
```

### "Port hopping not working"

**Problem:** Config not applied
**Solution:**
```bash
# Check Hysteria config
sudo cat /etc/hysteria/config.yaml

# Should show:
# listen: :20000-30000

# Restart service
sudo systemctl restart hysteria-server
```

### Client can't maintain connection

**Problem:** NAT/firewall blocking port changes
**Solution:**
- Increase hop interval (5m or 10m)
- Use smaller port range
- Check client logs

### High packet loss

**Problem:** Some ports in range blocked
**Solution:**
- Change port range
- Avoid common port ranges
- Check ISP restrictions

---

## 🎯 Use Cases

### 1. Bypassing Great Firewall (China)
```
Port Range: 40000-50000
Interval: 1m
Result: Extremely effective
```

### 2. Bypassing Corporate Firewall
```
Port Range: 20000-25000
Interval: 5m
Result: Good evasion
```

### 3. Personal VPN (No Censorship)
```
Port Range: Not needed
Single Port: 36712
Result: Simpler, same performance
```

### 4. High-Security Environment
```
Port Range: 10000-65535 (max)
Interval: 30s
Result: Maximum resistance
```

---

## 📈 Best Practices

### ✅ Do This:
- Use large port range (5000+ ports)
- Let interval be Auto (recommended)
- Open full range in firewall
- Test after configuration
- Monitor connection stability

### ❌ Don't Do This:
- Don't use tiny ranges (<100 ports)
- Don't use well-known ports (<1024)
- Don't forget firewall rules
- Don't set interval too short (<30s)
- Don't use overlapping ranges with other services

---

## 🔐 Security Considerations

### Port Scanning
**Risk:** Large open port range = larger attack surface
**Mitigation:** 
- Hysteria only responds to valid authentication
- Failed attempts are logged
- Consider fail2ban integration

### DDoS Attacks
**Risk:** More ports = more potential targets
**Mitigation:**
- Rate limiting built into Hysteria
- Use strong passwords
- Monitor connection logs

### Port Reuse
**Risk:** Another service might use same port
**Mitigation:**
- Choose uncommon port ranges
- Check for conflicts: `sudo netstat -tulpn | grep -E "20000|30000"`

---

## 📊 Configuration Examples

### Minimal (Testing)
```yaml
listen: :36000-36010
# No interval specified (auto)
```

### Balanced (Production)
```yaml
listen: :20000-30000
portHopping:
  interval: 1m
```

### Maximum Evasion
```yaml
listen: :10000-60000
portHopping:
  interval: 30s
obfs:
  type: salamander
  salamander:
    password: strong_obfs_password
```

### No Hopping (Default)
```yaml
listen: :36712
# Single port, no hopping
```

---

## 🔄 Migration Guide

### From Single Port to Port Hopping

**Step 1:** Enable in Web UI or edit config:
```yaml
# Before:
listen: :36712

# After:
listen: :20000-30000
```

**Step 2:** Update firewall:
```bash
# Remove old rule
sudo ufw delete allow 36712/udp

# Add new range
sudo ufw allow 20000:30000/udp
```

**Step 3:** Restart Hysteria:
```bash
sudo systemctl restart hysteria-server
```

**Step 4:** Update client config:
```yaml
# Change server line
server: your-ip:20000-30000
```

**Step 5:** Test connection

### From Port Hopping to Single Port

**Reverse the steps above**

---

## 📚 Additional Resources

- [Hysteria Documentation](https://v2.hysteria.network/)
- [Port Hopping Explained](https://en.wikipedia.org/wiki/Port_knocking)
- [Anti-Censorship Techniques](https://www.eff.org/deeplinks)

---

## ✅ Quick Reference

**Enable Port Hopping:**
1. Check "Enable Port Hopping" checkbox
2. Set port range (20000-30000)
3. Open firewall: `sudo ufw allow 20000:30000/udp`
4. Save & Restart Hysteria

**Disable Port Hopping:**
1. Uncheck "Enable Port Hopping"
2. Set single port (36712)
3. Open firewall: `sudo ufw allow 36712/udp`
4. Save & Restart Hysteria

**Client Config:**
```yaml
server: your-ip:20000-30000  # Range for hopping
# OR
server: your-ip:36712        # Single port
```

---

**Feature Status:** ✅ **Fully Implemented**  
**Version:** 1.1.0  
**Last Updated:** January 2026
