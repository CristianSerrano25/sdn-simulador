// Global variables
let eventSource = null;
let trafficChart = null;
let hostsChart = null;

// DOM elements
const startBtn = document.getElementById('startBtn');
const durationInput = document.getElementById('duration');
const simStatus = document.getElementById('simStatus');
const totalPackets = document.getElementById('totalPackets');
const activeHosts = document.getElementById('activeHosts');
const blockedHosts = document.getElementById('blockedHosts');
const attacksDetected = document.getElementById('attacksDetected');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const eventLog = document.getElementById('eventLog');

// Initialize charts
function initCharts() {
    // Traffic Chart
    const trafficCtx = document.getElementById('trafficChart').getContext('2d');
    trafficChart = new Chart(trafficCtx, {
        type: 'doughnut',
        data: {
            labels: ['Tráfico Normal', 'Tráfico de Ataque'],
            datasets: [{
                data: [0, 0],
                backgroundColor: [
                    'rgba(0, 217, 255, 0.7)',
                    'rgba(239, 68, 68, 0.7)'
                ],
                borderColor: [
                    'rgba(0, 217, 255, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a8b2d1',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });

    // Hosts Chart
    const hostsCtx = document.getElementById('hostsChart').getContext('2d');
    hostsChart = new Chart(hostsCtx, {
        type: 'bar',
        data: {
            labels: ['Activos', 'Bloqueados'],
            datasets: [{
                label: 'Hosts',
                data: [0, 0],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(239, 68, 68, 0.7)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#a8b2d1',
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(100, 116, 200, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#a8b2d1'
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Add log entry
function addLog(message, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    const timestamp = new Date().toLocaleTimeString('es-ES');
    entry.textContent = `[${timestamp}] ${message}`;
    eventLog.insertBefore(entry, eventLog.firstChild);
    
    // Keep only last 50 entries
    while (eventLog.children.length > 50) {
        eventLog.removeChild(eventLog.lastChild);
    }
}

// Update UI with simulation data
function updateUI(data) {
    // Update stats
    totalPackets.textContent = data.stats.total_packets.toLocaleString();
    activeHosts.textContent = data.stats.active_hosts;
    blockedHosts.textContent = data.stats.blocked_hosts;
    attacksDetected.textContent = data.stats.attacks_detected;

    // Update charts
    trafficChart.data.datasets[0].data = [
        data.stats.normal_packets,
        data.stats.attack_packets
    ];
    trafficChart.update('none');

    hostsChart.data.datasets[0].data = [
        data.stats.active_hosts,
        data.stats.blocked_hosts
    ];
    hostsChart.update('none');

    // Update status
    if (data.running) {
        simStatus.textContent = 'En Ejecución';
        simStatus.classList.add('running');
    } else {
        simStatus.textContent = 'Finalizada';
        simStatus.classList.remove('running');
    }

    // Update progress (simulated based on packets)
    if (data.running && data.duration > 0) {
        const estimatedProgress = Math.min(95, (data.stats.total_packets / (data.duration * 50)) * 100);
        progressFill.style.width = `${estimatedProgress}%`;
        progressText.textContent = `${Math.round(estimatedProgress)}%`;
    }

    // Update network topology
    updateTopology(data);
}

// Update network topology visualization
function updateTopology(data) {
    // Reset all hosts
    document.querySelectorAll('.host').forEach(host => {
        host.classList.remove('blocked');
    });

    // Mark blocked hosts (we know H6 is the attacker)
    if (data.stats.blocked_hosts > 0) {
        const h6 = document.querySelector('[data-host="H6"]');
        if (h6) {
            h6.classList.add('blocked');
        }
    }
}

// Start simulation
async function startSimulation() {
    const duration = parseInt(durationInput.value);
    
    if (duration < 1 || duration > 300) {
        addLog('Duración inválida (1-300 segundos)', 'error');
        return;
    }

    startBtn.disabled = true;
    addLog(`Iniciando simulación de ${duration} segundos...`, 'info');

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ duration })
        });

        const result = await response.json();

        if (result.status === 'success') {
            addLog(result.message, 'success');
            startEventStream();
        } else {
            addLog(result.message, 'error');
            startBtn.disabled = false;
        }
    } catch (error) {
        addLog(`Error al iniciar simulación: ${error.message}`, 'error');
        startBtn.disabled = false;
    }
}

// Start event stream
function startEventStream() {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource('/api/stream');

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateUI(data);

        // Check for completion
        if (!data.running && data.stats.total_packets > 0) {
            addLog('Simulación completada', 'success');
            progressFill.style.width = '100%';
            progressText.textContent = '100%';
            eventSource.close();
            startBtn.disabled = false;

            // Log detection results
            if (data.stats.attacks_detected > 0) {
                addLog(`⚠️ Se detectaron ${data.stats.attacks_detected} ataques`, 'warning');
                addLog(`🚫 ${data.stats.blocked_hosts} hosts bloqueados`, 'warning');
            }
        }
    };

    eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        eventSource.close();
        startBtn.disabled = false;
    };
}

// Event listeners
startBtn.addEventListener('click', startSimulation);

durationInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        startSimulation();
    }
});

// Initialize on load
window.addEventListener('load', () => {
    initCharts();
    addLog('Sistema inicializado y listo', 'success');
});
