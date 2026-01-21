import subprocess
from typing import List, Dict, Any, Optional


class FirewallManager:
    """Manages UFW firewall rules automatically"""
    
    def __init__(self):
        self.ufw_available = self._check_ufw()
        
    def _check_ufw(self) -> bool:
        """Check if UFW is installed and available"""
        try:
            result = subprocess.run(
                ['which', 'ufw'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def is_ufw_enabled(self) -> bool:
        """Check if UFW is enabled"""
        if not self.ufw_available:
            return False
        
        try:
            result = subprocess.run(
                ['ufw', 'status'],
                capture_output=True,
                text=True
            )
            return 'Status: active' in result.stdout
        except Exception:
            return False
    
    def allow_port(self, port: int, protocol: str = 'tcp', comment: str = '') -> bool:
        """Allow a single port through firewall"""
        if not self.ufw_available:
            return True  # No firewall, nothing to configure
        
        try:
            cmd = ['ufw', 'allow', f'{port}/{protocol}']
            if comment:
                cmd.extend(['comment', comment])
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Warning: Failed to configure firewall for port {port}: {e}")
            return False
    
    def allow_port_range(self, port_start: int, port_end: int, protocol: str = 'tcp', comment: str = '') -> bool:
        """Allow a port range through firewall"""
        if not self.ufw_available:
            return True
        
        try:
            cmd = ['ufw', 'allow', f'{port_start}:{port_end}/{protocol}']
            if comment:
                cmd.extend(['comment', comment])
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Warning: Failed to configure firewall for range {port_start}-{port_end}: {e}")
            return False
    
    def remove_port(self, port: int, protocol: str = 'tcp') -> bool:
        """Remove port from firewall"""
        if not self.ufw_available:
            return True
        
        try:
            subprocess.run(
                ['ufw', 'delete', 'allow', f'{port}/{protocol}'],
                check=False,  # Don't fail if rule doesn't exist
                capture_output=True
            )
            return True
        except Exception:
            return False
    
    def remove_port_range(self, port_start: int, port_end: int, protocol: str = 'tcp') -> bool:
        """Remove port range from firewall"""
        if not self.ufw_available:
            return True
        
        try:
            subprocess.run(
                ['ufw', 'delete', 'allow', f'{port_start}:{port_end}/{protocol}'],
                check=False,
                capture_output=True
            )
            return True
        except Exception:
            return False
    
    def get_rules(self) -> List[str]:
        """Get current UFW rules"""
        if not self.ufw_available:
            return ["UFW not available"]
        
        try:
            result = subprocess.run(
                ['ufw', 'status', 'numbered'],
                capture_output=True,
                text=True
            )
            return result.stdout.split('\n')
        except Exception:
            return []
    
    def configure_for_hysteria(self, port: Optional[int] = None, 
                              port_start: Optional[int] = None, 
                              port_end: Optional[int] = None) -> Dict[str, Any]:
        """Auto-configure firewall for Hysteria (single port or range)"""
        if port_start and port_end:
            # Port hopping mode - open range
            success = self.allow_port_range(
                port_start, 
                port_end, 
                'udp', 
                'Hysteria Port Hopping'
            )
            return {
                "success": success,
                "mode": "range",
                "ports": f"{port_start}-{port_end}/udp",
                "message": f"Opened UDP ports {port_start}-{port_end}" if success else "Failed to open port range"
            }
        elif port:
            # Single port mode
            success = self.allow_port(port, 'udp', 'Hysteria')
            return {
                "success": success,
                "mode": "single",
                "port": f"{port}/udp",
                "message": f"Opened UDP port {port}" if success else "Failed to open port"
            }
        else:
            return {
                "success": False,
                "message": "No port configuration provided"
            }
    
    def configure_for_vless(self, port: int) -> Dict[str, Any]:
        """Auto-configure firewall for VLESS"""
        success = self.allow_port(port, 'tcp', 'VLESS')
        return {
            "success": success,
            "port": f"{port}/tcp",
            "message": f"Opened TCP port {port}" if success else "Failed to open port"
        }


# Global instance
firewall_manager = FirewallManager()
