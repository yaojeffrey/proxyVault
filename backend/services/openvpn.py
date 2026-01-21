import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional
from config import get_settings

settings = get_settings()


class OpenVPNManager:
    """Manages OpenVPN client for outbound routing"""
    
    def __init__(self):
        self.config_path = Path(settings.OPENVPN_CONFIG)
        self.service_name = settings.OPENVPN_SERVICE
        self.auth_file = self.config_path.parent / "auth.txt"
        
    def get_status(self) -> Dict[str, Any]:
        """Get OpenVPN service status"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", self.service_name],
                capture_output=True,
                text=True
            )
            is_running = result.stdout.strip() == "active"
            
            # Check if tun0 interface exists (VPN connected)
            tun_result = subprocess.run(
                ["ip", "link", "show", "tun0"],
                capture_output=True,
                text=True
            )
            has_tunnel = tun_result.returncode == 0
            
            return {
                "running": is_running,
                "connected": has_tunnel,
                "service": self.service_name,
                "config_exists": self.config_path.exists()
            }
        except Exception as e:
            return {
                "running": False,
                "connected": False,
                "error": str(e)
            }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current OpenVPN configuration status"""
        return {
            "configured": self.config_path.exists(),
            "auth_configured": self.auth_file.exists()
        }
    
    def update_config(self, config_content: str, username: Optional[str] = None, 
                     password: Optional[str] = None) -> bool:
        """Update OpenVPN configuration"""
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write main config file
            with open(self.config_path, 'w') as f:
                f.write(config_content)
            
            # If username/password provided, create auth file
            if username and password:
                with open(self.auth_file, 'w') as f:
                    f.write(f"{username}\n{password}\n")
                
                # Secure the auth file
                os.chmod(self.auth_file, 0o600)
                
                # Update config to use auth file if not already specified
                if 'auth-user-pass' not in config_content:
                    with open(self.config_path, 'a') as f:
                        f.write(f"\nauth-user-pass {self.auth_file}\n")
            
            # Set proper permissions
            os.chmod(self.config_path, 0o600)
            
            return True
        except Exception as e:
            raise Exception(f"Failed to update OpenVPN config: {str(e)}")
    
    def control_service(self, action: str) -> str:
        """Control OpenVPN service (start/stop/restart/status)"""
        if action not in ["start", "stop", "restart", "status"]:
            raise ValueError(f"Invalid action: {action}")
        
        try:
            result = subprocess.run(
                ["systemctl", action, self.service_name],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout or f"Service {action} successful"
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to {action} OpenVPN: {e.stderr}")
    
    def get_vpn_ip(self) -> Optional[str]:
        """Get VPN tunnel IP address"""
        try:
            result = subprocess.run(
                ["ip", "-4", "addr", "show", "tun0"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Parse IP from output
                for line in result.stdout.split('\n'):
                    if 'inet ' in line:
                        ip = line.strip().split()[1].split('/')[0]
                        return ip
            return None
        except Exception:
            return None
