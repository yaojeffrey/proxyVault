# ProxyVault Monitoring System

## 📊 Overview

ProxyVault includes a comprehensive real-time monitoring system accessible through the web admin interface. Monitor system resources, network traffic, active connections, and service logs all from one dashboard.

---

## 🎯 Features

### 1. Real-time System Monitoring

**CPU Usage**
- Current CPU percentage
- Real-time sparkline graph
- Multi-core support

**Memory Usage**
- RAM usage percentage
- Available vs used memory
- Real-time sparkline graph

**Disk Usage**
- Disk space percentage
- Used vs total space
- Free space available

**System Uptime**
- Days, hours, minutes
- Boot time timestamp

### 2. Network Traffic Monitoring

**Real-time Bandwidth**
- Download speed (KB/s)
- Upload speed (KB/s)
- Interactive line chart with history

**Traffic Statistics**
- Total bytes received
- Total bytes sent
- Packets sent/received
- Network errors and drops

**Network Interfaces**
- List of all interfaces (eth0, tun0, etc.)
- IPv4 and IPv6 addresses
- Interface status (UP/DOWN)
- Speed information

### 3. Connection Monitoring

**Active Connections**
- Hysteria connections count
- VLESS connections count
- Total system connections

**Per-Protocol Tracking**
- Real-time connection counts
- Updates every 3 seconds

### 4. Service Logs Viewer

**Live Log Viewing**
- ProxyVault API logs
- Hysteria service logs
- VLESS (Xray) logs
- OpenVPN logs

**Features**
- Select service to view
- Choose number of lines (50, 100, 200, 500)
- Manual refresh button
- Auto-refresh mode (updates every 5 seconds)
- Scrollable log window
- Monospaced font for readability

---

## 🖥️ Access Monitoring

### Via Web Interface

1. Open admin panel: `http://YOUR_SERVER_IP:8000`
2. Login with credentials
3. Click **"Monitoring"** tab
4. View real-time data

### Dashboard Updates

- **Service status**: Updates every 10 seconds
- **Monitoring data**: Updates every 3 seconds
- **Charts**: Smooth animations
- **Historical data**: Last 60 data points (10 minutes)

---

## 📈 Charts & Graphs

### Bandwidth Chart (Main)
- **Type**: Line chart
- **Data**: Download and upload speeds
- **Update frequency**: Every 3 seconds
- **History**: Last 10 minutes
- **Y-axis**: KB/s
- **Colors**: Green (download), Red (upload)

### CPU Sparkline (Mini)
- **Type**: Line chart (compact)
- **Data**: CPU percentage
- **Update frequency**: Every 3 seconds
- **History**: Last 60 points
- **Range**: 0-100%

### Memory Sparkline (Mini)
- **Type**: Line chart (compact)
- **Data**: Memory percentage
- **Update frequency**: Every 3 seconds
- **History**: Last 60 points
- **Range**: 0-100%

---

## 🔧 API Endpoints

### Monitoring Statistics
```http
GET /api/monitoring/stats
```
Returns current system statistics:
- CPU usage
- Memory usage
- Disk usage
- Network bandwidth (in/out)
- Total bytes sent/received

**Response Example:**
```json
{
  "cpu": {
    "percent": 15.2,
    "count": 4
  },
  "memory": {
    "total": 8589934592,
    "available": 5368709120,
    "used": 3221225472,
    "percent": 37.5
  },
  "network": {
    "bandwidth_in": 125.5,
    "bandwidth_out": 45.2,
    "bytes_sent": 1073741824,
    "bytes_recv": 2147483648
  }
}
```

### Historical Data
```http
GET /api/monitoring/history
```
Returns last 60 data points:
- Bandwidth history
- CPU history
- Memory history

### Active Connections
```http
GET /api/monitoring/connections
```
Returns connection counts:
```json
{
  "hysteria": 5,
  "vless": 3,
  "total": 45
}
```

### Traffic Statistics
```http
GET /api/monitoring/traffic
```
Returns detailed traffic stats:
- Total bytes/packets sent/received
- Errors and drops

### Network Interfaces
```http
GET /api/monitoring/interfaces
```
Returns all network interfaces with addresses.

### System Uptime
```http
GET /api/monitoring/uptime
```
Returns system uptime information.

### Process Information
```http
GET /api/monitoring/process/{service}
```
Services: `hysteria`, `vless`, `openvpn`, `proxyvault`

Returns process details:
- PID
- CPU usage
- Memory usage
- Thread count
- Status

### Service Logs
```http
GET /api/logs/{service}?lines=50
```
Services: `hysteria`, `vless`, `openvpn`, `proxyvault`

Returns recent log lines.

---

## 🎨 UI Components

### Stat Cards
- Large value display
- Label and units
- Color-coded borders
- Mini charts for CPU/Memory

### Traffic Chart
- Full-width interactive chart
- Hover tooltips
- Legend toggle
- Smooth animations

### Logs Viewer
- Dark theme (console-style)
- Monospaced font
- Auto-scroll to bottom
- Selectable service and line count
- Auto-refresh toggle

### Network Interfaces
- Card-based layout
- Status indicators (🟢 UP / 🔴 DOWN)
- IPv4 and IPv6 addresses
- Clean typography

---

## 🔍 Monitoring Use Cases

### 1. Performance Troubleshooting
- Monitor CPU spikes during high traffic
- Identify memory leaks
- Track bandwidth usage patterns
- Detect network errors

### 2. Capacity Planning
- Historical trends for resource usage
- Peak usage identification
- Growth tracking

### 3. Service Health
- Verify services are running
- Check connection counts
- Monitor process resources
- Review error logs

### 4. Security Monitoring
- Track connection patterns
- Identify unusual traffic
- Monitor failed service starts
- Review authentication attempts in logs

### 5. Network Diagnostics
- Verify OpenVPN connection (tun0 interface)
- Check bandwidth availability
- Monitor packet loss
- Identify routing issues

---

## 📊 Data Collection

### How Data is Collected

**System Stats**: Uses `psutil` Python library
- CPU: `psutil.cpu_percent()`
- Memory: `psutil.virtual_memory()`
- Disk: `psutil.disk_usage()`
- Network: `psutil.net_io_counters()`

**Connections**: Uses `ss` command
- Filters by port
- Counts established connections

**Logs**: Uses `journalctl` command
- Service-specific logs
- Systemd journal integration

**Process Info**: Uses `psutil.Process()`
- PID from systemd
- Resource usage per process

### Data Retention

- **Historical charts**: Last 60 data points (~10 minutes)
- **Logs**: As configured in systemd (default: persistent)
- **No long-term storage**: All data is real-time/recent

---

## ⚙️ Configuration

### Monitoring Settings

No configuration required! Monitoring is enabled by default.

### Adjust Update Frequency

Edit `frontend/app.js`:

```javascript
// Dashboard updates (default: 10 seconds)
setInterval(updateDashboard, 10000);

// Monitoring updates (default: 3 seconds)
setInterval(updateMonitoring, 3000);

// Logs auto-refresh (default: 5 seconds)
logsAutoRefresh = setInterval(loadLogs, 5000);
```

### Chart History Length

Edit `backend/services/monitoring.py`:

```python
# Default: 60 data points (10 minutes at 10s intervals)
self.bandwidth_history = deque(maxlen=60)
self.cpu_history = deque(maxlen=60)
self.memory_history = deque(maxlen=60)
```

---

## 🐛 Troubleshooting

### Monitoring Not Loading

**Check backend is running:**
```bash
sudo systemctl status proxyvault
```

**Check API endpoint:**
```bash
curl -u admin:password http://localhost:8000/api/monitoring/stats
```

**Check browser console:**
- Press F12 → Console tab
- Look for JavaScript errors

### Charts Not Displaying

**Verify Chart.js is loaded:**
- Check browser Network tab
- CDN: `cdn.jsdelivr.net/npm/chart.js@4.4.1`

**Clear browser cache:**
- Ctrl+Shift+Delete
- Clear cached images and files

### Logs Not Showing

**Check permissions:**
```bash
# journalctl requires sudo/root or journal group
sudo usermod -a -G systemd-journal proxyvault
```

**Test manually:**
```bash
journalctl -u hysteria-server -n 50
```

### Connection Counts Show 0

**Check `ss` command:**
```bash
# Verify ss works
ss -tn 'sport = :36712'
```

**Check services are running:**
```bash
systemctl status hysteria-server
systemctl status xray
```

---

## 📱 Mobile View

Monitoring dashboard is fully responsive:
- Stacked layout on mobile
- Touch-friendly controls
- Scrollable charts
- Readable on small screens

---

## 🔐 Security

**Authentication Required**
- All monitoring endpoints require HTTP Basic Auth
- Same credentials as admin panel

**No Data Leaks**
- Monitoring data stays on server
- No external analytics
- No telemetry sent

**Log Safety**
- Logs may contain sensitive data
- Access restricted to authenticated users
- Consider sanitizing logs if sharing

---

## 🚀 Performance Impact

**Backend Resource Usage**
- CPU: Minimal (<1% typical)
- Memory: ~10MB for monitoring data
- Disk I/O: Minimal (only log reads)

**Network Overhead**
- API requests: ~1KB per update
- Chart updates: <5KB per cycle
- Total bandwidth: ~2KB/s typical

**Optimization Tips**
- Increase update intervals if needed
- Reduce historical data points
- Limit log lines retrieved
- Disable auto-refresh when not viewing

---

## 📚 Additional Resources

### Related Tools

**System Monitoring**
- htop: `sudo apt install htop`
- iftop: `sudo apt install iftop`
- netdata: Full monitoring stack

**Log Analysis**
- lnav: `sudo apt install lnav`
- tail: `tail -f /var/log/syslog`

### Further Reading

- [Chart.js Documentation](https://www.chartjs.org/)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [systemd Journal](https://www.freedesktop.org/software/systemd/man/journalctl.html)

---

## ✨ Future Enhancements

Planned monitoring features:

- [ ] **Alerts**: Email/webhook notifications
- [ ] **Historical database**: Long-term storage (InfluxDB)
- [ ] **Grafana integration**: Advanced dashboards
- [ ] **Per-client statistics**: Track individual users
- [ ] **Geolocation**: Map of connections
- [ ] **Export data**: CSV/JSON download
- [ ] **Custom metrics**: User-defined monitoring
- [ ] **Performance profiling**: Detailed analysis

---

**Monitoring System Version**: 1.0.0  
**Last Updated**: January 2026  
**Chart Library**: Chart.js 4.4.1  
**Backend**: Python psutil
