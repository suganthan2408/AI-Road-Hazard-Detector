const API_BASE = 'http://localhost:8000';
let map;
let markers = [];
let autoRefreshInterval;

// Initialize map
function initMap() {
    // Default to New York, but will update when potholes are loaded
    map = L.map('map').setView([40.7128, -74.0060], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Try to get user's location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const userLat = position.coords.latitude;
            const userLon = position.coords.longitude;
            map.setView([userLat, userLon], 15);
            
            // Add user location marker
            L.marker([userLat, userLon], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                })
            }).addTo(map).bindPopup('Your Location');
        });
    }
}

// Fetch pothole data
async function fetchPotholes() {
    try {
        const response = await fetch(`${API_BASE}/potholes`);
        const result = await response.json();
        
        if (result.status === 'success') {
            updateDashboard(result.data);
        }
    } catch (error) {
        console.error('Error fetching potholes:', error);
    }
}

// Update dashboard with data
function updateDashboard(potholes) {
    // Update statistics
    const total = potholes.length;
    const high = potholes.filter(p => p.severity === 'High').length;
    const medium = potholes.filter(p => p.severity === 'Medium').length;
    const low = potholes.filter(p => p.severity === 'Low').length;
    
    document.getElementById('totalCount').textContent = total;
    document.getElementById('highCount').textContent = high;
    document.getElementById('mediumCount').textContent = medium;
    document.getElementById('lowCount').textContent = low;
    
    // Update map
    updateMap(potholes);
    
    // Update list
    updateList(potholes);
}

// Update map markers
function updateMap(potholes) {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    if (potholes.length === 0) return;
    
    // Add new markers
    potholes.forEach(pothole => {
        const color = pothole.severity === 'High' ? 'red' : 
                     pothole.severity === 'Medium' ? 'orange' : 'blue';
        
        const marker = L.circleMarker([pothole.latitude, pothole.longitude], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
        
        // Add popup
        const popupContent = `
            <div style="text-align: center;">
                <strong>Pothole Detected</strong><br>
                <span style="color: ${color}; font-weight: bold;">${pothole.severity} Severity</span><br>
                <small>${new Date(pothole.timestamp).toLocaleString()}</small><br>
                <img src="${API_BASE}${pothole.image_url}" style="width: 150px; margin-top: 5px; border-radius: 5px;">
            </div>
        `;
        marker.bindPopup(popupContent);
        
        markers.push(marker);
    });
    
    // Fit map to markers
    if (markers.length > 0) {
        const group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

// Update pothole list
function updateList(potholes) {
    const listContainer = document.getElementById('potholeList');
    
    if (potholes.length === 0) {
        listContainer.innerHTML = '<div class="no-data">No potholes detected yet</div>';
        return;
    }
    
    // Sort by timestamp (newest first)
    potholes.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    listContainer.innerHTML = potholes.map(pothole => `
        <div class="pothole-item ${pothole.severity.toLowerCase()}">
            <div class="pothole-header">
                <strong>ID: ${pothole.id.substring(0, 8)}</strong>
                <span class="severity-badge ${pothole.severity.toLowerCase()}">${pothole.severity}</span>
            </div>
            <div class="pothole-info">
                📅 ${new Date(pothole.timestamp).toLocaleString()}<br>
                📍 Lat: ${pothole.latitude.toFixed(6)}, Lon: ${pothole.longitude.toFixed(6)}
            </div>
            <img src="${API_BASE}${pothole.image_url}" class="pothole-image" alt="Pothole">
        </div>
    `).join('');
}

// Refresh data
function refreshData() {
    fetchPotholes();
}

// Clear all potholes
async function clearAllPotholes() {
    if (!confirm('Are you sure you want to clear all pothole data?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/potholes`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            alert('All potholes cleared!');
            refreshData();
        }
    } catch (error) {
        console.error('Error clearing potholes:', error);
        alert('Failed to clear potholes');
    }
}

// Auto-refresh toggle
document.getElementById('autoRefresh').addEventListener('change', (e) => {
    if (e.target.checked) {
        autoRefreshInterval = setInterval(refreshData, 5000);
    } else {
        clearInterval(autoRefreshInterval);
    }
});

// Initialize
window.onload = () => {
    initMap();
    refreshData();
    autoRefreshInterval = setInterval(refreshData, 5000);
};
