# Test version of app.py for local Windows testing
# Uses mock services instead of systemctl

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import secrets
import os
from typing import Optional, Dict, Any
import uvicorn

# Use mock services for local testing
from mock_services import MockHysteriaManager, MockVLESSManager, MockOpenVPNManager, MockRoutingManager
from services.monitoring import monitoring_manager
from config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="ProxyVault API (Test Mode)",
    description="Multi-Protocol Proxy Manager - Local Testing",
    version="1.0.0-test"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Security
security = HTTPBasic()
settings = get_settings()

# Service managers (MOCKED for Windows testing)
hysteria_mgr = MockHysteriaManager()
vless_mgr = MockVLESSManager()
openvpn_mgr = MockOpenVPNManager()
routing_mgr = MockRoutingManager()

print("=" * 60)
print("🧪 ProxyVault - LOCAL TEST MODE")
print("=" * 60)
print("✅ Using MOCK services (no real systemctl)")
print("✅ Monitoring system: ACTIVE")
print("✅ Frontend: http://localhost:8000/static/index.html")
print("✅ API Docs: http://localhost:8000/docs")
print("=" * 60)


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
    action: str


# API Routes
@app.get("/")
async def root():
    return {
        "name": "ProxyVault API (Test Mode)",
        "version": "1.0.0-test",
        "status": "running",
        "mode": "mock_services",
        "frontend": "http://localhost:8000/static/index.html",
        "docs": "http://localhost:8000/docs"
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
    return hysteria_mgr.get_config()


@app.post("/api/hysteria/config", dependencies=[Depends(verify_credentials)])
async def update_hysteria_config(config: HysteriaConfig):
    try:
        hysteria_mgr.update_config(config.dict())
        return {"status": "success", "message": "Hysteria configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/hysteria/service", dependencies=[Depends(verify_credentials)])
async def control_hysteria_service(action: ServiceAction):
    try:
        result = hysteria_mgr.control_service(action.action)
        return {"status": "success", "action": action.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# VLESS endpoints
@app.get("/api/vless/config", dependencies=[Depends(verify_credentials)])
async def get_vless_config():
    return vless_mgr.get_config()


@app.post("/api/vless/config", dependencies=[Depends(verify_credentials)])
async def update_vless_config(config: VLESSConfig):
    try:
        vless_mgr.update_config(config.dict())
        return {"status": "success", "message": "VLESS configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vless/service", dependencies=[Depends(verify_credentials)])
async def control_vless_service(action: ServiceAction):
    try:
        result = vless_mgr.control_service(action.action)
        return {"status": "success", "action": action.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vless/generate-keys", dependencies=[Depends(verify_credentials)])
async def generate_vless_keys():
    try:
        keys = vless_mgr.generate_reality_keys()
        return {"status": "success", "keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# OpenVPN endpoints
@app.get("/api/openvpn/config", dependencies=[Depends(verify_credentials)])
async def get_openvpn_config():
    return openvpn_mgr.get_config()


@app.post("/api/openvpn/config", dependencies=[Depends(verify_credentials)])
async def update_openvpn_config(config: OpenVPNConfig):
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
    try:
        result = openvpn_mgr.control_service(action.action)
        return {"status": "success", "action": action.action, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Routing endpoints
@app.get("/api/routing/status", dependencies=[Depends(verify_credentials)])
async def get_routing_status():
    return {
        "enabled": routing_mgr.is_routing_enabled(),
        "rules": routing_mgr.get_routing_rules()
    }


@app.post("/api/routing/enable", dependencies=[Depends(verify_credentials)])
async def enable_routing():
    try:
        routing_mgr.enable_routing()
        return {"status": "success", "message": "Traffic routing enabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/routing/disable", dependencies=[Depends(verify_credentials)])
async def disable_routing():
    try:
        routing_mgr.disable_routing()
        return {"status": "success", "message": "Traffic routing disabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System endpoints
@app.get("/api/system/info", dependencies=[Depends(verify_credentials)])
async def get_system_info():
    import psutil
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('C:\\').total,
            "used": psutil.disk_usage('C:\\').used,
            "free": psutil.disk_usage('C:\\').free,
            "percent": psutil.disk_usage('C:\\').percent
        }
    }


# Monitoring endpoints
@app.get("/api/monitoring/stats", dependencies=[Depends(verify_credentials)])
async def get_monitoring_stats():
    return monitoring_manager.get_system_stats()


@app.get("/api/monitoring/history", dependencies=[Depends(verify_credentials)])
async def get_monitoring_history():
    return monitoring_manager.get_historical_data()


@app.get("/api/monitoring/connections", dependencies=[Depends(verify_credentials)])
async def get_connections():
    # Return mock data for Windows testing
    return {
        "hysteria": 3,
        "vless": 2,
        "total": 25
    }


@app.get("/api/monitoring/traffic", dependencies=[Depends(verify_credentials)])
async def get_traffic_stats():
    return monitoring_manager.get_traffic_stats()


@app.get("/api/monitoring/interfaces", dependencies=[Depends(verify_credentials)])
async def get_network_interfaces():
    return monitoring_manager.get_network_interfaces()


@app.get("/api/monitoring/uptime", dependencies=[Depends(verify_credentials)])
async def get_uptime():
    return monitoring_manager.get_uptime()


@app.get("/api/monitoring/process/{service}", dependencies=[Depends(verify_credentials)])
async def get_process_info(service: str):
    # Return mock data for Windows testing
    return {
        "pid": 1234,
        "cpu_percent": 2.5,
        "memory_mb": 45.2,
        "memory_percent": 1.8,
        "num_threads": 4,
        "num_fds": 12,
        "status": "running",
        "create_time": 1642800000
    }


@app.get("/api/logs/{service}", dependencies=[Depends(verify_credentials)])
async def get_service_logs(service: str, lines: int = 50):
    # Return mock logs for Windows testing
    import datetime
    now = datetime.datetime.now()
    
    mock_logs = []
    for i in range(lines):
        timestamp = (now - datetime.timedelta(minutes=lines-i)).strftime('%Y-%m-%d %H:%M:%S')
        mock_logs.append(f"{timestamp} [INFO] {service} service log entry {i+1}")
    
    return {"service": service, "logs": mock_logs}


if __name__ == "__main__":
    print("\n🚀 Starting ProxyVault Test Server...")
    print("📍 Access frontend: http://localhost:8000/static/index.html")
    print("📚 API docs: http://localhost:8000/docs")
    print("🔑 Username: admin")
    print("🔑 Password: admin123\n")
    
    uvicorn.run(
        "app_test:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
