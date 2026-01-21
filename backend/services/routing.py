import subprocess
from typing import Dict, Any, List
from config import get_settings

settings = get_settings()


class RoutingManager:
    """Manages iptables rules for routing proxy traffic through OpenVPN"""
    
    def __init__(self):
        self.hysteria_port = settings.HYSTERIA_PORT
        self.vless_port = settings.VLESS_PORT
        self.marker_file = "/etc/proxyvault/routing_enabled"
        
    def is_routing_enabled(self) -> bool:
        """Check if routing is currently enabled"""
        import os
        return os.path.exists(self.marker_file)
    
    def get_routing_rules(self) -> List[Dict[str, str]]:
        """Get current iptables routing rules"""
        try:
            result = subprocess.run(
                ["iptables", "-t", "nat", "-L", "POSTROUTING", "-n", "-v"],
                capture_output=True,
                text=True
            )
            
            rules = []
            for line in result.stdout.split('\n'):
                if 'proxyvault' in line.lower() or str(self.hysteria_port) in line or str(self.vless_port) in line:
                    rules.append({"rule": line.strip()})
            
            return rules
        except Exception as e:
            return [{"error": str(e)}]
    
    def enable_routing(self) -> bool:
        """Enable traffic routing through OpenVPN"""
        try:
            # Get OpenVPN interface (usually tun0)
            tun_interface = self._get_vpn_interface()
            if not tun_interface:
                raise Exception("OpenVPN interface not found. Ensure OpenVPN is connected.")
            
            # Enable IP forwarding
            subprocess.run(
                ["sysctl", "-w", "net.ipv4.ip_forward=1"],
                check=True,
                capture_output=True
            )
            
            # Make IP forwarding permanent
            self._update_sysctl_conf()
            
            # Add iptables rules to route proxy traffic through VPN
            # Mark packets from proxy services
            self._add_iptables_rule([
                "iptables", "-t", "mangle", "-A", "PREROUTING",
                "-p", "tcp", "--dport", str(self.hysteria_port),
                "-j", "MARK", "--set-mark", "1"
            ])
            
            self._add_iptables_rule([
                "iptables", "-t", "mangle", "-A", "PREROUTING",
                "-p", "tcp", "--dport", str(self.vless_port),
                "-j", "MARK", "--set-mark", "1"
            ])
            
            # Route marked packets through VPN
            subprocess.run(
                ["ip", "rule", "add", "fwmark", "1", "table", "100"],
                check=False,  # Don't fail if rule exists
                capture_output=True
            )
            
            subprocess.run(
                ["ip", "route", "add", "default", "dev", tun_interface, "table", "100"],
                check=False,  # Don't fail if route exists
                capture_output=True
            )
            
            # NAT outgoing traffic through VPN
            self._add_iptables_rule([
                "iptables", "-t", "nat", "-A", "POSTROUTING",
                "-o", tun_interface,
                "-j", "MASQUERADE"
            ])
            
            # Create marker file
            import os
            os.makedirs(os.path.dirname(self.marker_file), exist_ok=True)
            with open(self.marker_file, 'w') as f:
                f.write("enabled")
            
            return True
        except Exception as e:
            raise Exception(f"Failed to enable routing: {str(e)}")
    
    def disable_routing(self) -> bool:
        """Disable traffic routing"""
        try:
            # Remove mangle rules
            subprocess.run(
                ["iptables", "-t", "mangle", "-D", "PREROUTING",
                 "-p", "tcp", "--dport", str(self.hysteria_port),
                 "-j", "MARK", "--set-mark", "1"],
                check=False,
                capture_output=True
            )
            
            subprocess.run(
                ["iptables", "-t", "mangle", "-D", "PREROUTING",
                 "-p", "tcp", "--dport", str(self.vless_port),
                 "-j", "MARK", "--set-mark", "1"],
                check=False,
                capture_output=True
            )
            
            # Remove routing rules
            subprocess.run(
                ["ip", "rule", "del", "fwmark", "1", "table", "100"],
                check=False,
                capture_output=True
            )
            
            subprocess.run(
                ["ip", "route", "del", "default", "table", "100"],
                check=False,
                capture_output=True
            )
            
            # Remove NAT rules (find and delete)
            tun_interface = self._get_vpn_interface()
            if tun_interface:
                subprocess.run(
                    ["iptables", "-t", "nat", "-D", "POSTROUTING",
                     "-o", tun_interface, "-j", "MASQUERADE"],
                    check=False,
                    capture_output=True
                )
            
            # Remove marker file
            import os
            if os.path.exists(self.marker_file):
                os.remove(self.marker_file)
            
            return True
        except Exception as e:
            raise Exception(f"Failed to disable routing: {str(e)}")
    
    def _get_vpn_interface(self) -> str:
        """Get VPN interface name (usually tun0)"""
        try:
            result = subprocess.run(
                ["ip", "link", "show"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if 'tun' in line:
                    # Extract interface name
                    interface = line.split(':')[1].strip().split('@')[0]
                    return interface
            return None
        except Exception:
            return None
    
    def _add_iptables_rule(self, command: List[str]) -> None:
        """Add iptables rule, ignore if exists"""
        try:
            subprocess.run(command, check=False, capture_output=True)
        except Exception:
            pass
    
    def _update_sysctl_conf(self) -> None:
        """Make IP forwarding permanent in sysctl.conf"""
        sysctl_file = "/etc/sysctl.conf"
        try:
            with open(sysctl_file, 'r') as f:
                content = f.read()
            
            if 'net.ipv4.ip_forward=1' not in content:
                with open(sysctl_file, 'a') as f:
                    f.write('\n# Enable IP forwarding for ProxyVault\n')
                    f.write('net.ipv4.ip_forward=1\n')
        except Exception:
            pass  # Non-critical if this fails
