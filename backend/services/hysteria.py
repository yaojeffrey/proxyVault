import subprocess
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from config import get_settings

settings = get_settings()


class HysteriaManager:
    """Manages Hysteria 2 proxy service"""
    
    def __init__(self):
        self.config_path = Path(settings.HYSTERIA_CONFIG)
        self.service_name = settings.HYSTERIA_SERVICE
        
    def get_status(self) -> Dict[str, Any]:
        """Get Hysteria service status"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", self.service_name],
                capture_output=True,
                text=True
            )
            is_running = result.stdout.strip() == "active"
            
            return {
                "running": is_running,
                "service": self.service_name,
                "config_exists": self.config_path.exists()
            }
        except Exception as e:
            return {
                "running": False,
                "error": str(e)
            }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current Hysteria configuration"""
        if not self.config_path.exists():
            return {"configured": False}
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return {
                "configured": True,
                "config": config
            }
        except Exception as e:
            return {"configured": False, "error": str(e)}
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """Update Hysteria configuration"""
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Build Hysteria 2 configuration
            hysteria_config = {
                "listen": f":{config_data['port']}",
                "acme": {
                    "domains": [],  # Self-signed for now
                    "email": ""
                },
                "auth": {
                    "type": "password",
                    "password": config_data['password']
                }
            }
            
            # Add optional obfuscation
            if config_data.get('obfs'):
                hysteria_config["obfs"] = {
                    "type": "salamander",
                    "salamander": {
                        "password": config_data['obfs']
                    }
                }
            
            # Add bandwidth limits
            if config_data.get('bandwidth_up'):
                hysteria_config["bandwidth"] = {
                    "up": config_data['bandwidth_up'],
                    "down": config_data.get('bandwidth_down', '100 mbps')
                }
            
            # Write configuration
            with open(self.config_path, 'w') as f:
                yaml.dump(hysteria_config, f, default_flow_style=False)
            
            return True
        except Exception as e:
            raise Exception(f"Failed to update Hysteria config: {str(e)}")
    
    def control_service(self, action: str) -> str:
        """Control Hysteria service (start/stop/restart/status)"""
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
            raise Exception(f"Failed to {action} Hysteria: {e.stderr}")
