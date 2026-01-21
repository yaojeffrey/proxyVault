from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Admin credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # API settings
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    
    # Service ports
    HYSTERIA_PORT: int = 36712
    VLESS_PORT: int = 8443
    
    # Paths
    CONFIG_DIR: str = "/etc/proxyvault"
    HYSTERIA_CONFIG: str = "/etc/hysteria/config.yaml"
    VLESS_CONFIG: str = "/etc/xray/config.json"
    OPENVPN_CONFIG: str = "/etc/openvpn/client/client.conf"
    
    # Service names
    HYSTERIA_SERVICE: str = "hysteria-server"
    VLESS_SERVICE: str = "xray"
    OPENVPN_SERVICE: str = "openvpn-client@client"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
