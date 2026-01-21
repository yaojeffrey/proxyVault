# 🧪 Local Testing Guide

## ✅ Server is Running!

Your ProxyVault test server is now live at:

### 🌐 Access Points

**Frontend (Main UI):**
```
http://localhost:8000/static/index.html
```

**API Documentation (Interactive):**
```
http://localhost:8000/docs
```

**API Root:**
```
http://localhost:8000/
```

---

## 🔑 Login Credentials

**Username:** `admin`  
**Password:** `admin123`

---

## 🎯 What to Test

### 1. Dashboard
- ✅ Open http://localhost:8000/static/index.html
- ✅ Login with credentials
- ✅ See 4 service status cards (Hysteria, VLESS, OpenVPN, Routing)
- ✅ All should show "Offline" initially

### 2. Monitoring Tab ⭐ NEW!
- ✅ Click **"Monitoring"** tab
- ✅ See real-time CPU/Memory/Disk stats
- ✅ Watch bandwidth chart updating (should show your Windows network activity)
- ✅ See active connections (mocked as 3 Hysteria, 2 VLESS, 25 total)
- ✅ View network interfaces (should show your actual Windows adapters)
- ✅ Mini CPU and Memory sparkline charts

### 3. Hysteria Tab
- ✅ Click **"Hysteria"** tab
- ✅ Click **"Generate"** button for password
- ✅ Fill in port (default 36712)
- ✅ Click **"Save Configuration"**
- ✅ Click **"Start"** button
- ✅ Go back to Dashboard - Hysteria should show "Running" (green dot)

### 4. VLESS Tab
- ✅ Click **"VLESS"** tab
- ✅ Click **"Generate UUID"**
- ✅ Click **"Generate New Keys"** (for Reality)
- ✅ See private and public keys filled
- ✅ Click **"Save Configuration"**
- ✅ Click **"Start"**
- ✅ Dashboard should show VLESS running

### 5. OpenVPN Tab
- ✅ Paste any text in the config textarea (mock data is fine)
- ✅ Click **"Save & Connect"**
- ✅ Dashboard should show OpenVPN connected (green)

### 6. Routing Tab
- ✅ Click **"Routing"** tab
- ✅ Click **"Enable Routing"**
- ✅ Dashboard should show "Enabled" (green)
- ✅ Click **"Disable Routing"**
- ✅ Should show "Disabled"

### 7. Logs Tab ⭐ NEW!
- ✅ Click **"Logs"** tab
- ✅ Select different services from dropdown
- ✅ Change lines count (50, 100, 200, 500)
- ✅ Click **"Refresh"** button
- ✅ Click **"Auto-refresh"** toggle (logs should update every 5 seconds)
- ✅ See mock log entries with timestamps

---

## 🔍 What You'll See

### Real Data (Actual Windows System):
- ✅ CPU usage %
- ✅ Memory usage %
- ✅ Disk usage (C: drive)
- ✅ Network bandwidth (real network traffic)
- ✅ Network interfaces (your actual adapters)
- ✅ System uptime

### Mocked Data (Simulated for Windows):
- 🎭 Service start/stop (no real systemctl)
- 🎭 Active connections count (fixed numbers)
- 🎭 Process information (fake PIDs)
- 🎭 Service logs (generated mock entries)

---

## 📊 Monitoring System Features

### Live Charts
- **Bandwidth Chart**: Updates every 3 seconds with real network I/O
- **CPU Sparkline**: Shows CPU % trend over last 10 minutes
- **Memory Sparkline**: Shows memory % trend over last 10 minutes

### Stat Cards
- Large values with units
- Color-coded borders
- Real-time updates

### Auto-Refresh
- Dashboard: Every 10 seconds
- Monitoring: Every 3 seconds
- Logs (when enabled): Every 5 seconds

---

## 🧪 Testing Scenarios

### Scenario 1: Monitor Resource Usage
1. Open monitoring tab
2. Run a heavy application (browser with many tabs, video render, etc.)
3. Watch CPU and bandwidth charts spike in real-time

### Scenario 2: Configure Multiple Services
1. Configure Hysteria
2. Start it
3. Configure VLESS
4. Start it
5. Go to monitoring - see 2 services "running"

### Scenario 3: Test Routing
1. Start OpenVPN (mock)
2. Enable routing
3. Check routing status
4. See mock iptables rules

### Scenario 4: View Logs
1. Go to Logs tab
2. Switch between services
3. Enable auto-refresh
4. Watch logs scrolling
5. Change lines count

---

## 🌐 API Testing

### Using Browser

Visit: http://localhost:8000/docs

Interactive Swagger UI where you can:
- Test all API endpoints
- See request/response schemas
- Try authentication
- View all monitoring endpoints

### Using curl

```bash
# Get status
curl -u admin:admin123 http://localhost:8000/api/status

# Get monitoring stats
curl -u admin:admin123 http://localhost:8000/api/monitoring/stats

# Get historical data
curl -u admin:admin123 http://localhost:8000/api/monitoring/history

# Get connections
curl -u admin:admin123 http://localhost:8000/api/monitoring/connections

# Get logs
curl -u admin:admin123 http://localhost:8000/api/logs/hysteria?lines=50
```

---

## 🐛 Known Limitations (Test Mode)

### Won't Work on Windows:
❌ systemctl commands (using mocks instead)
❌ iptables rules (routing is simulated)
❌ journalctl logs (showing generated mock data)
❌ ss command for connections (showing fixed numbers)
❌ Real service processes (no Hysteria/Xray/OpenVPN binaries)

### Works Perfectly:
✅ Web UI and all interactions
✅ Configuration forms and validation
✅ Real-time monitoring (CPU, memory, disk, network)
✅ Chart animations and updates
✅ API endpoints and responses
✅ Authentication
✅ Frontend-backend communication

---

## 🛑 Stop the Server

To stop the test server:
1. Press `Ctrl+C` in the PowerShell window
2. Or I can stop it for you

---

## ✨ What This Demonstrates

### ✅ Complete UI/UX
- Modern, responsive interface
- Tab-based navigation
- Real-time updates
- Interactive charts
- Service controls

### ✅ Backend API
- RESTful endpoints
- Authentication working
- Monitoring data collection
- JSON responses

### ✅ Monitoring System
- Chart.js integration
- Real system metrics
- Historical data
- Live updates

### ✅ Production Ready
- Code structure
- Error handling
- Data flow
- User experience

---

## 📸 Take Screenshots!

This is perfect for:
- Project portfolio
- Documentation
- Showing features
- Demo videos

---

## 🚀 Next Steps

After testing locally:

1. **Looks good?** → Push to GitHub
2. **Want changes?** → I can modify features
3. **Ready for production?** → Deploy to Ubuntu server
4. **Need Ubuntu VM?** → I can help with setup

---

**Test Server Status:** 🟢 RUNNING  
**Access:** http://localhost:8000/static/index.html  
**Credentials:** admin / admin123

**Enjoy testing! 🎉**
