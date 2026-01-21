import subprocess
import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from config import get_settings

settings = get_settings()


class VLESSManager:
    """Manages VLESS + Reality proxy service (using Xray-core)"""
    
    def __init__(self):
        self.config_path = Path(settings.VLESS_CONFIG)
        self.service_name = settings.VLESS_SERVICE
        # Import firewall manager
        from services.firewall import firewall_manager
        self.firewall = firewall_manager
        
    def get_status(self) -> Dict[str, Any]:
        """Get VLESS service status"""
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
        """Get current VLESS configuration"""
        if not self.config_path.exists():
            return {"configured": False}
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return {
                "configured": True,
                "config": config
            }
        except Exception as e:
            return {"configured": False, "error": str(e)}
    
    def generate_reality_keys(self) -> Dict[str, str]:
        """Generate Reality key pair using xray"""
        try:
            result = subprocess.run(
                ["xray", "x25519"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output: "Private key: xxx\nPublic key: yyy"
            lines = result.stdout.strip().split('\n')
            private_key = lines[0].split(': ')[1]
            public_key = lines[1].split(': ')[1]
            
            return {
                "private_key": private_key,
                "public_key": public_key
            }
        except Exception as e:
            raise Exception(f"Failed to generate Reality keys: {str(e)}")
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """Update VLESS configuration"""
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate keys if not provided
            if not config_data.get('private_key') or not config_data.get('public_key'):
                keys = self.generate_reality_keys()
                config_data['private_key'] = keys['private_key']
                config_data['public_key'] = keys['public_key']
            
            # Build Xray configuration with VLESS + Reality
            xray_config = {
                "log": {
                    "loglevel": "warning"
                },
                "inbounds": [{
                    "port": config_data['port'],
                    "protocol": "vless",
                    "settings": {
                        "clients": [{
                            "id": config_data['uuid'],
                            "flow": "xtls-rprx-vision"
                        }],
                        "decryption": "none"
                    },
                    "streamSettings": {
                        "network": "tcp",
                        "security": "reality",
                        "realitySettings": {
                            "show": False,
                            "dest": config_data['reality_dest'],
                            "xver": 0,
                            "serverNames": config_data['reality_server_names'],
                            "privateKey": config_data['private_key'],
                            "shortIds": config_data['short_ids']
                        }
                    }
                }],
                "outbounds": [{
                    "protocol": "freedom",
                    "tag": "direct"
                }]
            }
            
            # Write configuration
            with open(self.config_path, 'w') as f:
                json.dump(xray_config, f, indent=2)
            
            # Auto-configure firewall
            self.firewall.configure_for_vless(config_data['port'])
            
            return True
        except Exception as e:
            raise Exception(f"Failed to update VLESS config: {str(e)}")
    
    def control_service(self, action: str) -> str:
        """Control VLESS service (start/stop/restart/status)"""
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
            raise Exception(f"Failed to {action} VLESS: {e.stderr}")
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a random UUID for VLESS"""
        return str(uuid.uuid4())
