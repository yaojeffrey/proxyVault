// API Configuration
const API_BASE = window.location.origin;
const API_USER = 'admin';  // Default, should be changed
const API_PASS = 'admin123';  // Default, should be changed

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Authorization': 'Basic ' + btoa(`${API_USER}:${API_PASS}`),
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Tab Management
document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        const targetTab = button.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(targetTab).classList.add('active');
    });
});

// Dashboard Status Updates
async function updateDashboard() {
    try {
        const status = await apiRequest('/api/status');
        
        // Update Hysteria status
        updateStatusCard('hysteria-status', status.hysteria.running);
        
        // Update VLESS status
        updateStatusCard('vless-status', status.vless.running);
        
        // Update OpenVPN status
        updateStatusCard('openvpn-status', status.openvpn.connected);
        
        // Update Routing status
        const routingCard = document.getElementById('routing-status');
        const routingDot = routingCard.querySelector('.status-dot');
        const routingText = routingCard.querySelector('.status-text');
        
        if (status.routing) {
            routingDot.classList.remove('offline');
            routingDot.classList.add('online');
            routingText.textContent = 'Enabled';
        } else {
            routingDot.classList.remove('online');
            routingDot.classList.add('offline');
            routingText.textContent = 'Disabled';
        }
    } catch (error) {
        console.error('Failed to update dashboard:', error);
    }
}

function updateStatusCard(cardId, isRunning) {
    const card = document.getElementById(cardId);
    const dot = card.querySelector('.status-dot');
    const text = card.querySelector('.status-text');
    
    if (isRunning) {
        dot.classList.remove('offline');
        dot.classList.add('online');
        text.textContent = 'Running';
    } else {
        dot.classList.remove('online');
        dot.classList.add('offline');
        text.textContent = 'Offline';
    }
}

// Hysteria Functions
document.getElementById('hysteria-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const config = {
        port: parseInt(document.getElementById('hysteria-port').value),
        password: document.getElementById('hysteria-password').value,
        obfs: document.getElementById('hysteria-obfs').value || null,
        bandwidth_up: document.getElementById('hysteria-bandwidth-up').value,
        bandwidth_down: document.getElementById('hysteria-bandwidth-down').value
    };
    
    try {
        await apiRequest('/api/hysteria/config', 'POST', config);
        showNotification('Hysteria configuration saved successfully!', 'success');
        updateDashboard();
    } catch (error) {
        showNotification('Failed to save Hysteria configuration', 'error');
    }
});

// VLESS Functions
document.getElementById('vless-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const serverNames = document.getElementById('vless-server-names').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s);
    
    const config = {
        port: parseInt(document.getElementById('vless-port').value),
        uuid: document.getElementById('vless-uuid').value,
        reality_dest: document.getElementById('vless-reality-dest').value,
        reality_server_names: serverNames,
        private_key: document.getElementById('vless-private-key').value || null,
        public_key: document.getElementById('vless-public-key').value || null,
        short_ids: [""]
    };
    
    try {
        await apiRequest('/api/vless/config', 'POST', config);
        showNotification('VLESS configuration saved successfully!', 'success');
        updateDashboard();
    } catch (error) {
        showNotification('Failed to save VLESS configuration', 'error');
    }
});

async function generateRealityKeys() {
    try {
        const result = await apiRequest('/api/vless/generate-keys', 'POST');
        document.getElementById('vless-private-key').value = result.keys.private_key;
        document.getElementById('vless-public-key').value = result.keys.public_key;
        showNotification('Reality keys generated!', 'success');
    } catch (error) {
        showNotification('Failed to generate keys', 'error');
    }
}

function generateUUID() {
    // Simple UUID v4 generator
    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
    document.getElementById('vless-uuid').value = uuid;
    showNotification('UUID generated!', 'info');
}

// OpenVPN Functions
document.getElementById('openvpn-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const config = {
        config_content: document.getElementById('openvpn-config').value,
        username: document.getElementById('openvpn-username').value || null,
        password: document.getElementById('openvpn-password').value || null
    };
    
    try {
        await apiRequest('/api/openvpn/config', 'POST', config);
        showNotification('OpenVPN configuration saved!', 'success');
        
        // Automatically try to start OpenVPN
        await controlService('openvpn', 'start');
    } catch (error) {
        showNotification('Failed to save OpenVPN configuration', 'error');
    }
});

function loadOpenVPNFile(input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('openvpn-config').value = e.target.result;
            showNotification('Config file loaded!', 'info');
        };
        reader.readAsText(file);
    }
}

// Service Control
async function controlService(service, action) {
    try {
        await apiRequest(`/api/${service}/service`, 'POST', { action });
        showNotification(`${service.toUpperCase()} ${action} successful!`, 'success');
        
        // Wait a moment for service to change state
        setTimeout(updateDashboard, 1000);
    } catch (error) {
        showNotification(`Failed to ${action} ${service.toUpperCase()}`, 'error');
    }
}

// Routing Functions
async function enableRouting() {
    try {
        await apiRequest('/api/routing/enable', 'POST');
        showNotification('Traffic routing enabled!', 'success');
        updateDashboard();
        loadRoutingInfo();
    } catch (error) {
        showNotification('Failed to enable routing. Is OpenVPN connected?', 'error');
    }
}

async function disableRouting() {
    try {
        await apiRequest('/api/routing/disable', 'POST');
        showNotification('Traffic routing disabled!', 'success');
        updateDashboard();
        loadRoutingInfo();
    } catch (error) {
        showNotification('Failed to disable routing', 'error');
    }
}

async function loadRoutingInfo() {
    try {
        const status = await apiRequest('/api/routing/status');
        const infoDiv = document.getElementById('routing-info');
        
        let html = '<h3>Routing Status</h3>';
        html += `<p><strong>Enabled:</strong> ${status.enabled ? 'Yes' : 'No'}</p>`;
        
        if (status.rules && status.rules.length > 0) {
            html += '<h4>Active Rules:</h4><pre>';
            status.rules.forEach(rule => {
                html += rule.rule + '\n';
            });
            html += '</pre>';
        }
        
        infoDiv.innerHTML = html;
    } catch (error) {
        console.error('Failed to load routing info:', error);
    }
}

// Helper Functions
function generatePassword(inputId) {
    const length = 16;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < length; i++) {
        password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    document.getElementById(inputId).value = password;
    showNotification('Password generated!', 'info');
}

// Load existing configurations on page load
async function loadConfigurations() {
    try {
        // Load Hysteria config
        const hysteriaConfig = await apiRequest('/api/hysteria/config');
        if (hysteriaConfig.configured && hysteriaConfig.config) {
            const config = hysteriaConfig.config;
            if (config.listen) {
                const port = config.listen.replace(':', '');
                document.getElementById('hysteria-port').value = port;
            }
            if (config.auth && config.auth.password) {
                document.getElementById('hysteria-password').value = config.auth.password;
            }
            if (config.obfs && config.obfs.salamander) {
                document.getElementById('hysteria-obfs').value = config.obfs.salamander.password;
            }
            if (config.bandwidth) {
                document.getElementById('hysteria-bandwidth-up').value = config.bandwidth.up || '100 mbps';
                document.getElementById('hysteria-bandwidth-down').value = config.bandwidth.down || '100 mbps';
            }
        }
        
        // Load VLESS config
        const vlessConfig = await apiRequest('/api/vless/config');
        if (vlessConfig.configured && vlessConfig.config) {
            const config = vlessConfig.config;
            if (config.inbounds && config.inbounds.length > 0) {
                const inbound = config.inbounds[0];
                document.getElementById('vless-port').value = inbound.port;
                
                if (inbound.settings.clients && inbound.settings.clients.length > 0) {
                    document.getElementById('vless-uuid').value = inbound.settings.clients[0].id;
                }
                
                if (inbound.streamSettings.realitySettings) {
                    const reality = inbound.streamSettings.realitySettings;
                    document.getElementById('vless-reality-dest').value = reality.dest;
                    document.getElementById('vless-server-names').value = reality.serverNames.join(', ');
                    document.getElementById('vless-private-key').value = reality.privateKey;
                    // Public key not stored in config, would need to regenerate or derive
                }
            }
        }
    } catch (error) {
        console.error('Failed to load configurations:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    loadConfigurations();
    loadRoutingInfo();
    
    // Auto-refresh dashboard every 10 seconds
    setInterval(updateDashboard, 10000);
});
