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

// Toggle port hopping UI
function togglePortHopping() {
    const enabled = document.getElementById('hysteria-port-hopping').checked;
    document.getElementById('single-port-config').style.display = enabled ? 'none' : 'block';
    document.getElementById('port-hopping-config').style.display = enabled ? 'block' : 'none';
}

document.getElementById('hysteria-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const portHoppingEnabled = document.getElementById('hysteria-port-hopping').checked;
    
    const config = {
        password: document.getElementById('hysteria-password').value,
        obfs: document.getElementById('hysteria-obfs').value || null,
        bandwidth_up: document.getElementById('hysteria-bandwidth-up').value,
        bandwidth_down: document.getElementById('hysteria-bandwidth-down').value,
        port_hopping_enabled: portHoppingEnabled
    };
    
    if (portHoppingEnabled) {
        // Port hopping configuration
        config.port_start = parseInt(document.getElementById('hysteria-port-start').value);
        config.port_end = parseInt(document.getElementById('hysteria-port-end').value);
        config.port_hop_interval = document.getElementById('hysteria-hop-interval').value || null;
        config.port = config.port_start; // Default for API compatibility
    } else {
        // Single port configuration
        config.port = parseInt(document.getElementById('hysteria-port').value);
    }
    
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
    
    // Auto-reveal password after generation
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
    }
    
    showNotification('Password generated!', 'info');
}

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = event.target;
    
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '🙈 Hide';
    } else {
        input.type = 'password';
        button.textContent = '👁️ Show';
    }
}

function copyToClipboard(inputId) {
    const input = document.getElementById(inputId);
    input.select();
    document.execCommand('copy');
    showNotification('Copied to clipboard!', 'success');
}

// Export Configuration
async function exportConfig(protocol) {
    try {
        const result = await apiRequest(`/api/export/${protocol}`);
        
        if (!result || !result.formats) {
            showNotification('No configuration to export', 'error');
            return;
        }
        
        // Create modal to show export options
        showExportModal(protocol, result);
        
    } catch (error) {
        showNotification(`Failed to export ${protocol} configuration`, 'error');
    }
}

function showExportModal(protocol, data) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'export-modal';
    
    let content = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>📤 Export ${protocol.toUpperCase()} Configuration</h2>
                <button class="modal-close" onclick="closeExportModal()">✖</button>
            </div>
            <div class="modal-body">
                <p><strong>Server IP:</strong> ${data.server_ip}</p>
                <hr>
    `;
    
    if (protocol === 'hysteria') {
        content += `
                <h3>📋 Client Config (YAML)</h3>
                <p><small>Copy this to your Hysteria client config file:</small></p>
                <textarea readonly rows="12" onclick="this.select()">${data.formats.yaml}</textarea>
                <button class="btn-secondary" onclick="copyTextArea(this.previousElementSibling)">📋 Copy YAML</button>
                
                <hr>
                
                <h3>🔗 Quick Import URI</h3>
                <p><small>Use this for clients that support URI import:</small></p>
                <input type="text" readonly value="${data.formats.uri}" onclick="this.select()">
                <button class="btn-secondary" onclick="copyToClipboardValue('${data.formats.uri}')">📋 Copy URI</button>
        `;
    } else if (protocol === 'vless') {
        content += `
                <h3>🔗 VLESS URI (for Nekobox/v2rayN)</h3>
                <p><small>Import this URI directly into your client:</small></p>
                <textarea readonly rows="3" onclick="this.select()">${data.formats.uri}</textarea>
                <button class="btn-secondary" onclick="copyTextArea(this.previousElementSibling)">📋 Copy URI</button>
                
                <hr>
                
                <h3>📝 Manual Configuration</h3>
                <pre>${data.formats.text}</pre>
                <button class="btn-secondary" onclick="copyText(\`${data.formats.text}\`)">📋 Copy Text</button>
        `;
    }
    
    content += `
            </div>
        </div>
    `;
    
    modal.innerHTML = content;
    document.body.appendChild(modal);
    
    // Show modal
    setTimeout(() => modal.classList.add('show'), 10);
}

function closeExportModal() {
    const modal = document.getElementById('export-modal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }
}

function copyTextArea(textarea) {
    textarea.select();
    document.execCommand('copy');
    showNotification('Copied to clipboard!', 'success');
}

function copyToClipboardValue(text) {
    const temp = document.createElement('textarea');
    temp.value = text;
    document.body.appendChild(temp);
    temp.select();
    document.execCommand('copy');
    document.body.removeChild(temp);
    showNotification('Copied to clipboard!', 'success');
}

function copyText(text) {
    const temp = document.createElement('textarea');
    temp.value = text;
    document.body.appendChild(temp);
    temp.select();
    document.execCommand('copy');
    document.body.removeChild(temp);
    showNotification('Copied to clipboard!', 'success');
}

// Load existing configurations on page load
async function loadConfigurations() {
    try {
        // Load Hysteria config
        const hysteriaConfig = await apiRequest('/api/hysteria/config');
        if (hysteriaConfig.configured && hysteriaConfig.config) {
            const config = hysteriaConfig.config;
            
            // Check if port hopping is enabled
            if (config.listen && config.listen.includes('-')) {
                // Port hopping mode
                const [start, end] = config.listen.replace(':', '').split('-');
                document.getElementById('hysteria-port-hopping').checked = true;
                document.getElementById('hysteria-port-start').value = start;
                document.getElementById('hysteria-port-end').value = end;
                
                // Load hop interval if present
                if (config.portHopping && config.portHopping.interval) {
                    document.getElementById('hysteria-hop-interval').value = config.portHopping.interval;
                }
                
                togglePortHopping(); // Show port hopping UI
            } else if (config.listen) {
                // Single port mode
                const port = config.listen.replace(':', '');
                document.getElementById('hysteria-port').value = port;
                document.getElementById('hysteria-port-hopping').checked = false;
                togglePortHopping(); // Show single port UI
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

// ============================================
// MONITORING FUNCTIONS
// ============================================

let bandwidthChart, cpuChart, memoryChart;
let logsAutoRefresh = null;

// Initialize Charts
function initializeCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };

    // Bandwidth Chart
    const bandwidthCtx = document.getElementById('chart-bandwidth');
    if (bandwidthCtx) {
        bandwidthChart = new Chart(bandwidthCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Download (KB/s)',
                        data: [],
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Upload (KB/s)',
                        data: [],
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                ...commonOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + ' KB/s';
                            }
                        }
                    }
                }
            }
        });
    }

    // CPU Chart (mini sparkline)
    const cpuCtx = document.getElementById('chart-cpu');
    if (cpuCtx) {
        cpuChart = new Chart(cpuCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU %',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { display: false, beginAtZero: true, max: 100 }
                }
            }
        });
    }

    // Memory Chart (mini sparkline)
    const memoryCtx = document.getElementById('chart-memory');
    if (memoryCtx) {
        memoryChart = new Chart(memoryCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Memory %',
                    data: [],
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.2)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { display: false, beginAtZero: true, max: 100 }
                }
            }
        });
    }
}

// Update Monitoring Data
async function updateMonitoring() {
    try {
        // Get system stats
        const stats = await apiRequest('/api/monitoring/stats');
        
        // Update stat values
        document.getElementById('stat-cpu').textContent = stats.cpu.percent.toFixed(1) + '%';
        document.getElementById('stat-memory').textContent = stats.memory.percent.toFixed(1) + '%';
        document.getElementById('stat-disk').textContent = stats.disk.percent.toFixed(1) + '%';
        document.getElementById('stat-download').textContent = stats.network.bandwidth_in + ' KB/s';
        document.getElementById('stat-upload').textContent = stats.network.bandwidth_out + ' KB/s';
        
        // Format bytes
        document.getElementById('stat-total-rx').textContent = formatBytes(stats.network.bytes_recv);
        document.getElementById('stat-total-tx').textContent = formatBytes(stats.network.bytes_sent);
        
        // Disk details
        document.getElementById('disk-details').textContent = 
            `${formatBytes(stats.disk.used)} / ${formatBytes(stats.disk.total)}`;
        
        // Get historical data
        const history = await apiRequest('/api/monitoring/history');
        
        // Update bandwidth chart
        if (bandwidthChart && history.bandwidth.length > 0) {
            bandwidthChart.data.labels = history.bandwidth.map(d => d.time);
            bandwidthChart.data.datasets[0].data = history.bandwidth.map(d => d.in);
            bandwidthChart.data.datasets[1].data = history.bandwidth.map(d => d.out);
            bandwidthChart.update('none');
        }
        
        // Update CPU chart
        if (cpuChart && history.cpu.length > 0) {
            cpuChart.data.labels = history.cpu.map(d => d.time);
            cpuChart.data.datasets[0].data = history.cpu.map(d => d.value);
            cpuChart.update('none');
        }
        
        // Update Memory chart
        if (memoryChart && history.memory.length > 0) {
            memoryChart.data.labels = history.memory.map(d => d.time);
            memoryChart.data.datasets[0].data = history.memory.map(d => d.value);
            memoryChart.update('none');
        }
        
        // Get connections
        const connections = await apiRequest('/api/monitoring/connections');
        document.getElementById('conn-hysteria').textContent = connections.hysteria;
        document.getElementById('conn-vless').textContent = connections.vless;
        document.getElementById('conn-total').textContent = connections.total;
        
        // Get uptime
        const uptime = await apiRequest('/api/monitoring/uptime');
        document.getElementById('stat-uptime').textContent = uptime.formatted;
        document.getElementById('uptime-details').textContent = `Since ${uptime.boot_time}`;
        
        // Get network interfaces
        const interfaces = await apiRequest('/api/monitoring/interfaces');
        updateInterfacesList(interfaces);
        
    } catch (error) {
        console.error('Failed to update monitoring:', error);
    }
}

function updateInterfacesList(interfaces) {
    const container = document.getElementById('interfaces-list');
    if (!container) return;
    
    let html = '';
    for (const [name, info] of Object.entries(interfaces)) {
        const statusClass = info.is_up ? '' : 'down';
        const statusText = info.is_up ? '🟢 UP' : '🔴 DOWN';
        
        html += `
            <div class="interface-card ${statusClass}">
                <h4>${name} ${statusText}</h4>
                ${info.addresses.map(addr => `
                    <div class="address">${addr.type}: ${addr.address}</div>
                `).join('')}
            </div>
        `;
    }
    container.innerHTML = html;
}

// Format bytes to human-readable
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Logs Functions
async function loadLogs() {
    const service = document.getElementById('log-service').value;
    const lines = document.getElementById('log-lines').value;
    const output = document.getElementById('logs-output');
    
    try {
        output.textContent = 'Loading logs...';
        const result = await apiRequest(`/api/logs/${service}?lines=${lines}`);
        
        if (result.logs && result.logs.length > 0) {
            output.textContent = result.logs.join('\n');
            // Auto-scroll to bottom
            output.parentElement.scrollTop = output.parentElement.scrollHeight;
        } else {
            output.textContent = 'No logs available';
        }
    } catch (error) {
        output.textContent = `Error loading logs: ${error.message}`;
    }
}

function toggleAutoRefresh() {
    const btn = document.getElementById('auto-refresh-btn');
    
    if (logsAutoRefresh) {
        clearInterval(logsAutoRefresh);
        logsAutoRefresh = null;
        btn.textContent = '▶️ Auto-refresh';
        btn.parentElement.classList.remove('btn-success');
        btn.parentElement.classList.add('btn-secondary');
    } else {
        loadLogs(); // Load immediately
        logsAutoRefresh = setInterval(loadLogs, 5000); // Refresh every 5 seconds
        btn.textContent = '⏸️ Stop refresh';
        btn.parentElement.classList.remove('btn-secondary');
        btn.parentElement.classList.add('btn-success');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    loadConfigurations();
    loadRoutingInfo();
    
    // Initialize charts
    initializeCharts();
    
    // Initial monitoring update
    updateMonitoring();
    
    // Auto-refresh dashboard every 10 seconds
    setInterval(updateDashboard, 10000);
    
    // Auto-refresh monitoring every 3 seconds
    setInterval(updateMonitoring, 3000);
    
    // Load logs initially
    loadLogs();
});
