# Mock service managers for local testing on Windows
# This replaces systemctl calls with simulated responses

class MockServiceManager:
    """Base mock service manager"""
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.is_running = False
        
    def get_status(self):
        return {
            "running": self.is_running,
            "service": self.service_name,
            "config_exists": True
        }
    
    def get_config(self):
        return {
            "configured": True,
            "config": {
                "message": "Mock configuration for local testing"
            }
        }
    
    def update_config(self, config_data):
        print(f"[MOCK] Updating {self.service_name} config:", config_data)
        return True
    
    def control_service(self, action):
        print(f"[MOCK] {action} {self.service_name}")
        if action == "start":
            self.is_running = True
        elif action == "stop":
            self.is_running = False
        elif action == "restart":
            self.is_running = True
        return f"Service {action} successful (mocked)"

class MockHysteriaManager(MockServiceManager):
    def __init__(self):
        super().__init__("hysteria-server")

class MockVLESSManager(MockServiceManager):
    def __init__(self):
        super().__init__("xray")
    
    def generate_reality_keys(self):
        return {
            "private_key": "mock_private_key_1234567890abcdef",
            "public_key": "mock_public_key_0987654321fedcba"
        }
    
    @staticmethod
    def generate_uuid():
        import uuid
        return str(uuid.uuid4())

class MockOpenVPNManager(MockServiceManager):
    def __init__(self):
        super().__init__("openvpn-client")
        self.connected = False
    
    def get_status(self):
        return {
            "running": self.is_running,
            "connected": self.connected,
            "service": self.service_name,
            "config_exists": True
        }
    
    def update_config(self, config_content, username=None, password=None):
        print(f"[MOCK] OpenVPN config updated (length: {len(config_content)} chars)")
        return True
    
    def control_service(self, action):
        result = super().control_service(action)
        if action == "start":
            self.connected = True
        elif action == "stop":
            self.connected = False
        return result

class MockRoutingManager:
    def __init__(self):
        self.enabled = False
    
    def is_routing_enabled(self):
        return self.enabled
    
    def get_routing_rules(self):
        if self.enabled:
            return [
                {"rule": "Chain POSTROUTING (mock rule 1)"},
                {"rule": "Chain PREROUTING (mock rule 2)"}
            ]
        return []
    
    def enable_routing(self):
        print("[MOCK] Enabling traffic routing")
        self.enabled = True
        return True
    
    def disable_routing(self):
        print("[MOCK] Disabling traffic routing")
        self.enabled = False
        return True
