import base64
import json
from typing import Dict, Any, Optional
from urllib.parse import quote


class ConfigExporter:
    """Export proxy configurations for client applications"""
    
    @staticmethod
    def export_hysteria(config_data: Dict[str, Any], server_ip: str) -> Dict[str, Any]:
        """Export Hysteria configuration in multiple formats"""
        
        # Determine port string
        if config_data.get('port_hopping_enabled'):
            port_str = f"{config_data['port_start']}-{config_data['port_end']}"
        else:
            port_str = str(config_data['port'])
        
        # Hysteria 2 YAML config
        yaml_config = f"""server: {server_ip}:{port_str}

auth: {config_data['password']}

bandwidth:
  up: {config_data.get('bandwidth_up', '100 mbps')}
  down: {config_data.get('bandwidth_down', '100 mbps')}
"""
        
        if config_data.get('obfs'):
            yaml_config += f"""
obfs:
  type: salamander
  salamander:
    password: {config_data['obfs']}
"""
        
        yaml_config += """
socks5:
  listen: 127.0.0.1:1080

http:
  listen: 127.0.0.1:8080
"""
        
        # Hysteria 2 URI (for some clients)
        # Format: hysteria2://password@server:port/?obfs=salamander&obfs-password=xxx
        # Password must be URL-encoded to handle special characters
        encoded_password = quote(config_data['password'], safe='')
        uri_parts = [f"hysteria2://{encoded_password}@{server_ip}:{port_str}"]
        params = []
        
        if config_data.get('obfs'):
            params.append(f"obfs=salamander")
            params.append(f"obfs-password={quote(config_data['obfs'], safe='')}")
        
        if params:
            uri = uri_parts[0] + "/?" + "&".join(params)
        else:
            uri = uri_parts[0]
        
        return {
            "yaml": yaml_config,
            "uri": uri,
            "json": {
                "server": f"{server_ip}:{port_str}",
                "auth": config_data['password'],
                "bandwidth": {
                    "up": config_data.get('bandwidth_up', '100 mbps'),
                    "down": config_data.get('bandwidth_down', '100 mbps')
                },
                "obfs": config_data.get('obfs'),
                "socks5": {"listen": "127.0.0.1:1080"},
                "http": {"listen": "127.0.0.1:8080"}
            }
        }
    
    @staticmethod
    def export_vless(config_data: Dict[str, Any], server_ip: str) -> Dict[str, Any]:
        """Export VLESS configuration in multiple formats"""
        
        # VLESS URI format
        # vless://uuid@server:port?encryption=none&flow=xtls-rprx-vision&security=reality&sni=xxx&fp=chrome&pbk=xxx&type=tcp#Name
        
        params = [
            "encryption=none",
            "flow=xtls-rprx-vision",
            "security=reality",
            f"sni={config_data['reality_server_names'][0]}",
            "fp=chrome",
            f"pbk={config_data['public_key']}",
            "type=tcp",
            f"sid="  # Short ID, empty is valid
        ]
        
        uri = f"vless://{config_data['uuid']}@{server_ip}:{config_data['port']}?" + "&".join(params) + "#ProxyVault-VLESS"
        
        # JSON config for v2rayN/Nekobox
        json_config = {
            "protocol": "vless",
            "address": server_ip,
            "port": config_data['port'],
            "id": config_data['uuid'],
            "flow": "xtls-rprx-vision",
            "encryption": "none",
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "serverName": config_data['reality_server_names'][0],
                "fingerprint": "chrome",
                "publicKey": config_data['public_key'],
                "shortId": "",
                "spiderX": ""
            }
        }
        
        # Human-readable text format
        text_config = f"""Protocol: VLESS
Address: {server_ip}
Port: {config_data['port']}
UUID: {config_data['uuid']}
Flow: xtls-rprx-vision
Encryption: none
Network: tcp
Security: reality
SNI: {config_data['reality_server_names'][0]}
Fingerprint: chrome
Public Key: {config_data['public_key']}
Short ID: (empty)
"""
        
        return {
            "uri": uri,
            "json": json_config,
            "text": text_config,
            "qr_data": uri  # For QR code generation
        }
    
    @staticmethod
    def get_server_ip() -> str:
        """Get server's public IP address"""
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-s', 'ifconfig.me'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
        return "YOUR_SERVER_IP"


# Global instance
config_exporter = ConfigExporter()
