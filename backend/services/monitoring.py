import subprocess
import psutil
import time
from typing import Dict, Any, List
from pathlib import Path
from collections import deque
from datetime import datetime

class MonitoringManager:
    """Manages system and service monitoring"""
    
    def __init__(self):
        # Store historical data (last 60 data points = 10 minutes at 10s intervals)
        self.bandwidth_history = deque(maxlen=60)
        self.cpu_history = deque(maxlen=60)
        self.memory_history = deque(maxlen=60)
        self.last_net_io = None
        self.last_check_time = None
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network I/O
        net_io = psutil.net_io_counters()
        
        # Calculate bandwidth (bytes per second)
        bandwidth_in = 0
        bandwidth_out = 0
        if self.last_net_io and self.last_check_time:
            time_diff = time.time() - self.last_check_time
            if time_diff > 0:
                bandwidth_in = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
                bandwidth_out = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
        
        self.last_net_io = net_io
        self.last_check_time = time.time()
        
        # Store history
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.bandwidth_history.append({
            'time': timestamp,
            'in': round(bandwidth_in / 1024, 2),  # KB/s
            'out': round(bandwidth_out / 1024, 2)
        })
        self.cpu_history.append({
            'time': timestamp,
            'value': cpu_percent
        })
        self.memory_history.append({
            'time': timestamp,
            'value': memory.percent
        })
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'network': {
                'bandwidth_in': round(bandwidth_in / 1024, 2),  # KB/s
                'bandwidth_out': round(bandwidth_out / 1024, 2),
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        }
    
    def get_historical_data(self) -> Dict[str, Any]:
        """Get historical monitoring data"""
        return {
            'bandwidth': list(self.bandwidth_history),
            'cpu': list(self.cpu_history),
            'memory': list(self.memory_history)
        }
    
    def get_service_connections(self, port: int) -> int:
        """Count active connections to a specific port"""
        try:
            result = subprocess.run(
                ['ss', '-tn', f'sport = :{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Count lines (excluding header)
            lines = result.stdout.strip().split('\n')
            return max(0, len(lines) - 1)
        except Exception:
            return 0
    
    def get_all_connections(self) -> Dict[str, int]:
        """Get connection counts for all services"""
        from config import get_settings
        settings = get_settings()
        
        return {
            'hysteria': self.get_service_connections(settings.HYSTERIA_PORT),
            'vless': self.get_service_connections(settings.VLESS_PORT),
            'total': len(psutil.net_connections(kind='inet'))
        }
    
    def get_service_logs(self, service_name: str, lines: int = 50) -> List[str]:
        """Get recent logs for a service"""
        try:
            result = subprocess.run(
                ['journalctl', '-u', service_name, '-n', str(lines), '--no-pager'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            return []
        except Exception as e:
            return [f"Error fetching logs: {str(e)}"]
    
    def get_process_info(self, service_name: str) -> Dict[str, Any]:
        """Get detailed process information for a service"""
        try:
            # Get PID from systemd
            result = subprocess.run(
                ['systemctl', 'show', service_name, '--property=MainPID'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pid_line = result.stdout.strip()
                pid = int(pid_line.split('=')[1])
                
                if pid > 0 and psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    
                    # Get process stats
                    with process.oneshot():
                        return {
                            'pid': pid,
                            'cpu_percent': process.cpu_percent(interval=0.1),
                            'memory_mb': process.memory_info().rss / 1024 / 1024,
                            'memory_percent': process.memory_percent(),
                            'num_threads': process.num_threads(),
                            'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0,
                            'status': process.status(),
                            'create_time': process.create_time()
                        }
        except Exception as e:
            pass
        
        return {
            'pid': 0,
            'cpu_percent': 0,
            'memory_mb': 0,
            'memory_percent': 0,
            'num_threads': 0,
            'num_fds': 0,
            'status': 'not_running',
            'create_time': 0
        }
    
    def get_network_interfaces(self) -> Dict[str, Any]:
        """Get information about network interfaces"""
        interfaces = {}
        
        for interface, addrs in psutil.net_if_addrs().items():
            stats = psutil.net_if_stats().get(interface)
            
            interfaces[interface] = {
                'addresses': [],
                'is_up': stats.isup if stats else False,
                'speed': stats.speed if stats else 0
            }
            
            for addr in addrs:
                if addr.family == 2:  # AF_INET (IPv4)
                    interfaces[interface]['addresses'].append({
                        'type': 'IPv4',
                        'address': addr.address,
                        'netmask': addr.netmask
                    })
                elif addr.family == 10:  # AF_INET6 (IPv6)
                    interfaces[interface]['addresses'].append({
                        'type': 'IPv6',
                        'address': addr.address
                    })
        
        return interfaces
    
    def get_traffic_stats(self) -> Dict[str, Any]:
        """Get detailed traffic statistics"""
        net_io = psutil.net_io_counters()
        
        return {
            'total_bytes_sent': net_io.bytes_sent,
            'total_bytes_recv': net_io.bytes_recv,
            'total_packets_sent': net_io.packets_sent,
            'total_packets_recv': net_io.packets_recv,
            'errors_in': net_io.errin,
            'errors_out': net_io.errout,
            'drops_in': net_io.dropin,
            'drops_out': net_io.dropout
        }
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get system uptime"""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return {
            'seconds': int(uptime_seconds),
            'formatted': f"{days}d {hours}h {minutes}m",
            'boot_time': datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')
        }

# Global instance
monitoring_manager = MonitoringManager()
