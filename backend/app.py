from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import secrets
import os
from typing import Optional, Dict, Any
import uvicorn

from services.hysteria import HysteriaManager
from services.vless import VLESSManager
from services.openvpn import OpenVPNManager
from services.routing import RoutingManager
from services.monitoring import monitoring_manager
from services.export import config_exporter
from services.firewall import firewall_manager
from config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="ProxyVault API",
    description="Multi-Protocol Proxy Manager with OpenVPN Routing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBasic()
settings = get_settings()

# Service managers
hysteria_mgr = HysteriaManager()
vless_mgr = VLESSManager()
openvpn_mgr = OpenVPNManager()
routing_mgr = RoutingManager()

# Mount static files (frontend)
# Check if frontend directory exists relative to backend
import pathlib
frontend_path = pathlib.Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
else:
    print(f"Warning: Frontend directory not found at {frontend_path}")


# Authentication
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Pydantic models
class HysteriaConfig(BaseModel):
    port: int = 36712
    password: str
    obfs: Optional[str] = None
    bandwidth_up: Optional[str] = "100 mbps"
    bandwidth_down: Optional[str] = "100 mbps"
    # Port hopping settings
    port_hopping_enabled: bool = False
    port_start: Optional[int] = 20000
    port_end: Optional[int] = 30000
    port_hop_interval: Optional[str] = None  # e.g., "30s", "1m", "5m"


class VLESSConfig(BaseModel):
    port: int = 8443
    uuid: str
    reality_dest: str = "www.microsoft.com:443"
    reality_server_names: list[str] = ["www.microsoft.com"]
    private_key: Optional[str] = None
    public_key: Optional[str] = None
    short_ids: list[str] = [""]


class OpenVPNConfig(BaseModel):
    config_content: str
    username: Optional[str] = None
    password: Optional[str] = None


class ServiceAction(BaseModel):
    action: str  # start, stop, restart, status


# API Routes

@app.get("/")
async def root():
    return {
        "name": "ProxyVault API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/status", dependencies=[Depends(verify_credentials)])
async def get_status():
    """Get status of all services"""
    return {
        "hysteria": hysteria_mgr.get_status(),
        "vless": vless_mgr.get_status(),
        "openvpn": openvpn_mgr.get_status(),
        "routing": routing_mgr.is_routing_enabled()
    }


# Hysteria endpoints
@app.get("/api/hysteria/config", dependencies=[Depends(verify_credentials)])
async def get_hysteria_config():
    """Get current Hysteria configuration"""
    return hysteria_mgr.get_config()


@app.post("/api/hysteria/config", dependencies=[Depends(verify_credentials)])
async def update_hysteria_config(config: HysteriaConfig):
    """Update Hysteria configuration"""
    try:
        hysteria_mgr.update_config(config.dict())
        return {"status": "success", "message": "Hysteria configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/hysteria/service", dependencies=[Depends(verify_credentials)])
async def control_hysteria_service(action: ServiceAction):
    """Control Hysteria service (start/stop/restart)"""
    try:
        result = hysteria_mgr.control_service(action.action)
        return {"status": "success", "action": action.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# VLESS endpoints
@app.get("/api/vless/config", dependencies=[Depends(verify_credentials)])
async def get_vless_config():
    """Get current VLESS configuration"""
    return vless_mgr.get_config()


@app.post("/api/vless/config", dependencies=[Depends(verify_credentials)])
async def update_vless_config(config: VLESSConfig):
    """Update VLESS configuration"""
    try:
        vless_mgr.update_config(config.dict())
        return {"status": "success", "message": "VLESS configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vless/service", dependencies=[Depends(verify_credentials)])
async def control_vless_service(action: ServiceAction):
    """Control VLESS service (start/stop/restart)"""
    try:
        result = vless_mgr.control_service(action.action)
        return {"status": "success", "action": action.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vless/generate-keys", dependencies=[Depends(verify_credentials)])
async def generate_vless_keys():
    """Generate new Reality key pair"""
    try:
        keys = vless_mgr.generate_reality_keys()
        return {"status": "success", "keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# OpenVPN endpoints
@app.get("/api/openvpn/config", dependencies=[Depends(verify_credentials)])
async def get_openvpn_config():
    """Get current OpenVPN configuration status"""
    return openvpn_mgr.get_config()


@app.post("/api/openvpn/config", dependencies=[Depends(verify_credentials)])
async def update_openvpn_config(config: OpenVPNConfig):
    """Upload OpenVPN configuration"""
    try:
        openvpn_mgr.update_config(
            config.config_content,
            config.username,
            config.password
        )
        return {"status": "success", "message": "OpenVPN configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/openvpn/service", dependencies=[Depends(verify_credentials)])
async def control_openvpn_service(action: ServiceAction):
    """Control OpenVPN service (start/stop/restart)"""
    try:
        result = openvpn_mgr.control_service(action.action)
        return {"status": "success", "action": action.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Routing endpoints
@app.get("/api/routing/status", dependencies=[Depends(verify_credentials)])
async def get_routing_status():
    """Get traffic routing status"""
    return {
        "enabled": routing_mgr.is_routing_enabled(),
        "rules": routing_mgr.get_routing_rules()
    }


@app.post("/api/routing/enable", dependencies=[Depends(verify_credentials)])
async def enable_routing():
    """Enable traffic routing through OpenVPN"""
    try:
        routing_mgr.enable_routing()
        return {"status": "success", "message": "Traffic routing enabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/routing/disable", dependencies=[Depends(verify_credentials)])
async def disable_routing():
    """Disable traffic routing"""
    try:
        routing_mgr.disable_routing()
        return {"status": "success", "message": "Traffic routing disabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System endpoints
@app.get("/api/system/info", dependencies=[Depends(verify_credentials)])
async def get_system_info():
    """Get system information"""
    import psutil
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        }
    }


# Monitoring endpoints
@app.get("/api/monitoring/stats", dependencies=[Depends(verify_credentials)])
async def get_monitoring_stats():
    """Get comprehensive system statistics"""
    return monitoring_manager.get_system_stats()


@app.get("/api/monitoring/history", dependencies=[Depends(verify_credentials)])
async def get_monitoring_history():
    """Get historical monitoring data"""
    return monitoring_manager.get_historical_data()


@app.get("/api/monitoring/connections", dependencies=[Depends(verify_credentials)])
async def get_connections():
    """Get active connections count"""
    return monitoring_manager.get_all_connections()


@app.get("/api/monitoring/traffic", dependencies=[Depends(verify_credentials)])
async def get_traffic_stats():
    """Get detailed traffic statistics"""
    return monitoring_manager.get_traffic_stats()


@app.get("/api/monitoring/interfaces", dependencies=[Depends(verify_credentials)])
async def get_network_interfaces():
    """Get network interfaces information"""
    return monitoring_manager.get_network_interfaces()


@app.get("/api/monitoring/uptime", dependencies=[Depends(verify_credentials)])
async def get_uptime():
    """Get system uptime"""
    return monitoring_manager.get_uptime()


@app.get("/api/monitoring/process/{service}", dependencies=[Depends(verify_credentials)])
async def get_process_info(service: str):
    """Get process information for a service"""
    service_map = {
        'hysteria': settings.HYSTERIA_SERVICE,
        'vless': settings.VLESS_SERVICE,
        'openvpn': settings.OPENVPN_SERVICE,
        'proxyvault': 'proxyvault'
    }
    
    service_name = service_map.get(service)
    if not service_name:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return monitoring_manager.get_process_info(service_name)


@app.get("/api/logs/{service}", dependencies=[Depends(verify_credentials)])
async def get_service_logs(service: str, lines: int = 50):
    """Get recent logs for a service"""
    service_map = {
        'hysteria': settings.HYSTERIA_SERVICE,
        'vless': settings.VLESS_SERVICE,
        'openvpn': settings.OPENVPN_SERVICE,
        'proxyvault': 'proxyvault'
    }
    
    service_name = service_map.get(service)
    if not service_name:
        raise HTTPException(status_code=404, detail="Service not found")
    
    logs = monitoring_manager.get_service_logs(service_name, lines)
    return {"service": service, "logs": logs}


# Export endpoints
@app.get("/api/export/hysteria", dependencies=[Depends(verify_credentials)])
async def export_hysteria_config():
    """Export Hysteria configuration for client apps"""
    try:
        hysteria_config = hysteria_mgr.get_config()
        if not hysteria_config.get('configured'):
            raise HTTPException(status_code=404, detail="Hysteria not configured yet")
        
        # Get server IP
        server_ip = config_exporter.get_server_ip()
        
        # Parse config for export
        config = hysteria_config['config']
        port_str = config.get('listen', ':36712').replace(':', '')
        
        export_data = {
            'password': config.get('auth', {}).get('password', ''),
            'bandwidth_up': config.get('bandwidth', {}).get('up', '100 mbps'),
            'bandwidth_down': config.get('bandwidth', {}).get('down', '100 mbps'),
            'obfs': config.get('obfs', {}).get('salamander', {}).get('password')
        }
        
        # Check if port hopping
        if '-' in port_str:
            parts = port_str.split('-')
            export_data['port_hopping_enabled'] = True
            export_data['port_start'] = int(parts[0])
            export_data['port_end'] = int(parts[1])
        else:
            export_data['port_hopping_enabled'] = False
            export_data['port'] = int(port_str)
        
        result = config_exporter.export_hysteria(export_data, server_ip)
        return {
            "status": "success",
            "server_ip": server_ip,
            "formats": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/vless", dependencies=[Depends(verify_credentials)])
async def export_vless_config():
    """Export VLESS configuration for client apps"""
    try:
        vless_config = vless_mgr.get_config()
        if not vless_config.get('configured'):
            raise HTTPException(status_code=404, detail="VLESS not configured yet")
        
        # Get server IP
        server_ip = config_exporter.get_server_ip()
        
        # Parse config for export
        config = vless_config['config']
        inbound = config['inbounds'][0]
        reality = inbound['streamSettings']['realitySettings']
        
        export_data = {
            'port': inbound['port'],
            'uuid': inbound['settings']['clients'][0]['id'],
            'reality_server_names': reality['serverNames'],
            'public_key': reality['privateKey']  # Note: We need to derive public from private
        }
        
        result = config_exporter.export_vless(export_data, server_ip)
        return {
            "status": "success",
            "server_ip": server_ip,
            "formats": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Firewall management endpoints
@app.get("/api/firewall/status", dependencies=[Depends(verify_credentials)])
async def get_firewall_status():
    """Get firewall status and rules"""
    return {
        "available": firewall_manager.ufw_available,
        "enabled": firewall_manager.is_ufw_enabled(),
        "rules": firewall_manager.get_rules()
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True
    )
