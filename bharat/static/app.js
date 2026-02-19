// SentinelOps Dashboard Core v3.0
document.addEventListener('DOMContentLoaded', () => {

    // -------------------------------------------------------------------------
    // 1. Initial State
    // -------------------------------------------------------------------------
    const API_BASE = '/api';
    const REFRESH_RATE = 3000;

    // -------------------------------------------------------------------------
    // 2. Chart Configurations
    // -------------------------------------------------------------------------

    // 2.1 Main Timeline Chart
    const ctxMain = document.getElementById('main-timeline-chart').getContext('2d');
    const gradSky = ctxMain.createLinearGradient(0, 0, 0, 400);
    gradSky.addColorStop(0, 'rgba(14, 165, 233, 0.15)');
    gradSky.addColorStop(1, 'rgba(14, 165, 233, 0)');

    const mainChart = new Chart(ctxMain, {
        type: 'line',
        data: {
            labels: Array(50).fill(''),
            datasets: [
                {
                    label: 'CPU Load (%)',
                    data: Array(50).fill(0),
                    borderColor: '#0ea5e9',
                    borderWidth: 2,
                    backgroundColor: gradSky,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: 'RAM Sync (%)',
                    data: Array(50).fill(0),
                    borderColor: '#a855f7',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { display: false },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: '#64748b', font: { size: 10, family: 'JetBrains Mono' } }
                }
            },
            plugins: { legend: { display: false } },
            interaction: { mode: 'index', intersect: false }
        }
    });

    // 2.2 Radar Chart
    const ctxRadar = document.getElementById('radar-chart').getContext('2d');
    const radarChart = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: ['CPU', 'RAM', 'NET', 'DISK', 'ERR'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: 'rgba(14, 165, 233, 0.1)',
                borderColor: '#0ea5e9',
                pointBackgroundColor: '#0ea5e9',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.05)' },
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    pointLabels: { color: '#64748b', font: { size: 10 } },
                    ticks: { display: false },
                    suggestedMin: 0, suggestedMax: 100
                }
            },
            plugins: { legend: { display: false } }
        }
    });

    // 2.3 Sparklines
    const createSpark = (id, color) => {
        return new Chart(document.getElementById(id).getContext('2d'), {
            type: 'line',
            data: { labels: Array(10).fill(''), datasets: [{ data: [], borderColor: color, borderWidth: 2, pointRadius: 0, fill: false, tension: 0.4 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false, min: 0, max: 100 } } }
        });
    };
    const cpuSpark = createSpark('cpu-sparkline', '#0ea5e9');
    const memSpark = createSpark('mem-sparkline', '#a855f7');

    // -------------------------------------------------------------------------
    // 3. Data Sync Engine
    // -------------------------------------------------------------------------

    async function sync() {
        try {
            const [health, risk, metrics, incidents] = await Promise.all([
                fetch(`${API_BASE}/health`).then(r => r.json()),
                fetch(`${API_BASE}/risk/current`).then(r => r.json()),
                fetch(`${API_BASE}/metrics/recent`).then(r => r.json()),
                fetch(`${API_BASE}/incidents`).then(r => r.json())
            ]);

            updateUI(health, risk, metrics, incidents);
        } catch (e) {
            console.error('Core sync error:', e);
        }
    }

    function updateUI(health, risk, metrics, incidents) {
        const latest = metrics[0] || {};

        // 1. Numeric Values
        document.getElementById('health-val').textContent = Math.round(health.health_score || 0);
        document.getElementById('health-bar').style.width = (health.health_score || 0) + '%';

        document.getElementById('cpu-val').textContent = Math.round(latest.cpu || 0) + '%';
        document.getElementById('mem-val').textContent = Math.round(latest.memory || 0) + '%';

        // 2. Risk Panel
        const rPanel = document.getElementById('risk-panel');
        const rStatus = document.getElementById('risk-status');
        const rMsg = document.getElementById('risk-msg');
        const rIcon = document.getElementById('risk-icon');

        if (risk.latest_incident) {
            rStatus.textContent = risk.severity + " Alert";
            rMsg.textContent = risk.latest_incident;

            if (risk.severity === 'CRITICAL' || risk.severity === 'HIGH') {
                rPanel.className = 'glass-panel p-6 border-l-4 border-l-rose-500 bg-rose-500/10 shadow-lg shadow-rose-500/10';
                rIcon.className = 'fas fa-triangle-exclamation text-rose-500';
            } else {
                rPanel.className = 'glass-panel p-6 border-l-4 border-l-amber-500 bg-amber-500/5';
                rIcon.className = 'fas fa-shield-virus text-amber-500';
            }
        } else {
            rPanel.className = 'glass-panel p-6 border-l-4 border-l-emerald-500 bg-emerald-500/5';
            rStatus.textContent = "Secure";
            rMsg.textContent = "All protocols operational.";
            rIcon.className = 'fas fa-shield-check text-emerald-400';
        }

        // 3. Charts Update
        if (metrics.length > 0) {
            const rev = [...metrics].reverse();
            const cpuData = rev.map(m => m.cpu);
            const memData = rev.map(m => m.memory);

            mainChart.data.datasets[0].data = cpuData;
            mainChart.data.datasets[1].data = memData;
            mainChart.update('none');

            radarChart.data.datasets[0].data = [
                latest.cpu,
                latest.memory,
                latest.error_rate * 1000, // Normalized
                latest.disk,
                Math.min(100, latest.response_time / 10)
            ];
            radarChart.update('none');

            cpuSpark.data.datasets[0].data = cpuData.slice(-10);
            cpuSpark.update('none');
            memSpark.data.datasets[0].data = memData.slice(-10);
            memSpark.update('none');
        }

        // 4. Incident Log
        const log = document.getElementById('incident-rows');
        if (incidents.length === 0) {
            log.innerHTML = '<tr><td colspan="5" class="px-8 py-10 text-center text-slate-500">Sentinel heartbeat stable. No recent anomalies.</td></tr>';
        } else {
            log.innerHTML = incidents.map(i => `
                <tr class="hover:bg-white/5 transition-colors">
                    <td class="px-8 py-4 text-slate-500">#${i.id}</td>
                    <td class="px-8 py-4">
                        <span class="px-2 py-1 rounded-md text-[9px] font-bold border ${getSevClass(i.severity)}">${i.severity}</span>
                    </td>
                    <td class="px-8 py-4">
                        <div class="flex items-center space-x-2">
                            <span class="w-1.5 h-1.5 rounded-full ${i.status === 'OPEN' ? 'bg-rose-500 animate-pulse' : 'bg-slate-700'}"></span>
                            <span class="uppercase tracking-tighter ${i.status === 'OPEN' ? 'text-rose-400' : 'text-slate-500'}">${i.status}</span>
                        </div>
                    </td>
                    <td class="px-8 py-4 text-slate-200">${i.root_cause || 'Analyzing pattern...'}</td>
                    <td class="px-8 py-4 text-slate-500">${i.created_at}</td>
                </tr>
            `).join('');
        }
    }

    function getSevClass(sev) {
        if (sev === 'CRITICAL') return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
        if (sev === 'HIGH') return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
        return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
    }

    // Interactive Toggles
    window.toggleDataset = (idx) => {
        const ds = mainChart.data.datasets[idx];
        ds.hidden = !ds.hidden;
        mainChart.update();
    };

    window.focusMetric = (type) => {
        if (type === 'cpu') {
            mainChart.data.datasets[0].hidden = false;
            mainChart.data.datasets[1].hidden = true;
        } else {
            mainChart.data.datasets[0].hidden = true;
            mainChart.data.datasets[1].hidden = false;
        }
        mainChart.update();
    };

    // Clock
    setInterval(() => {
        document.getElementById('current-time').textContent = new Date().toLocaleTimeString('en-US', { hour12: false });
    }, 1000);

    // Initial and periodic sync
    sync();
    setInterval(sync, REFRESH_RATE);
});
