// SentinelOps Dashboard Logic
document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------------------
    // Configuration & State
    // -------------------------------------------------------------------------
    const REFRESH_INTERVAL = 3000; // 3 seconds
    let cpuHistory = [];
    let memHistory = [];
    let errorHistory = [];
    let labels = [];

    // -------------------------------------------------------------------------
    // Chart Initialization
    // -------------------------------------------------------------------------
    const chartCtx = document.getElementById('main-metrics-chart').getContext('2d');
    const mainChart = new Chart(chartCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'CPU Usage',
                    data: cpuHistory,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    label: 'Memory',
                    data: memHistory,
                    borderColor: '#818cf8',
                    backgroundColor: 'rgba(129, 140, 248, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    label: 'Error Rate',
                    data: errorHistory,
                    borderColor: '#f43f5e',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4,
                    borderWidth: 1,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b', font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });

    // Sparklines for CPU and MEM cards
    const createSparkline = (id, color) => {
        return new Chart(document.getElementById(id), {
            type: 'line',
            data: { labels: Array(10).fill(''), datasets: [{ data: [], borderColor: color, borderWidth: 2, pointRadius: 0, fill: false, tension: 0.4 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false, min: 0, max: 100 } } }
        });
    };

    const cpuSpark = createSparkline('cpu-sparkline', '#38bdf8');
    const memSpark = createSparkline('mem-sparkline', '#818cf8');

    // -------------------------------------------------------------------------
    // API data Fetching
    // -------------------------------------------------------------------------

    async function fetchData() {
        try {
            // Parallel fetches
            const [healthRes, riskRes, metricsRes, incidentsRes] = await Promise.all([
                fetch('/api/health'),
                fetch('/api/risk/current'),
                fetch('/api/metrics/recent'),
                fetch('/api/incidents')
            ]);

            const health = await healthRes.json();
            const risk = await riskRes.json();
            const metrics = await metricsRes.json();
            const incidents = await incidentsRes.json();

            updateHealthUI(health);
            updateRiskUI(risk);
            updateMetricsUI(metrics);
            updateIncidentsUI(incidents);
            
            // Re-sync success state
            document.getElementById('system-status-pulse').className = 'status-pulse';
            if (health.status === 'DEGRADED') document.getElementById('system-status-pulse').classList.add('warning');
            if (health.status === 'CRITICAL') document.getElementById('system-status-pulse').classList.add('critical');
            document.getElementById('system-status-text').textContent = `System ${health.status || 'Active'}`;
            document.getElementById('system-status-text').className = 
                health.status === 'HEALTHY' ? 'text-emerald-400' : 
                (health.status === 'DEGRADED' ? 'text-amber-400' : 'text-rose-400');

        } catch (err) {
            console.error('Fetch error:', err);
            document.getElementById('system-status-text').textContent = 'Connection Lost';
            document.getElementById('system-status-text').className = 'text-slate-500';
            document.getElementById('system-status-pulse').className = 'status-pulse critical';
        }
    }

    function updateHealthUI(data) {
        const score = Math.round(data.health_score || 0);
        document.getElementById('health-score').textContent = score;
        const ring = document.getElementById('health-ring');
        ring.setAttribute('stroke-dasharray', `${score}, 100`);
        
        const label = document.getElementById('health-label');
        label.textContent = data.status || 'UNKNOWN';
        
        if (score > 70) {
            ring.className.baseVal = 'text-emerald-500';
            label.className = 'text-[10px] font-semibold text-emerald-400 uppercase';
        } else if (score > 40) {
            ring.className.baseVal = 'text-amber-500';
            label.className = 'text-[10px] font-semibold text-amber-400 uppercase';
        } else {
            ring.className.baseVal = 'text-rose-500';
            label.className = 'text-[10px] font-semibold text-rose-400 uppercase';
        }
    }

    function updateRiskUI(data) {
        const messageEl = document.getElementById('risk-message');
        const detailsEl = document.getElementById('risk-details');
        const cardEl = document.getElementById('risk-card');
        const iconEl = document.getElementById('risk-icon');

        if (data.latest_incident) {
            messageEl.textContent = data.latest_incident;
            detailsEl.classList.remove('hidden');
            document.getElementById('risk-severity').textContent = data.severity;
            document.getElementById('risk-timestamp').textContent = data.timestamp;

            if (data.severity === 'HIGH' || data.severity === 'CRITICAL') {
                cardEl.className = 'glass-card p-6 border-l-4 border-l-rose-500 bg-rose-500/5';
                iconEl.className = 'fas fa-triangle-exclamation text-rose-500';
                document.getElementById('risk-severity').className = 'inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-500 uppercase tracking-tighter';
            } else {
                cardEl.className = 'glass-card p-6 border-l-4 border-l-amber-500 bg-amber-500/5';
                iconEl.className = 'fas fa-circle-exclamation text-amber-500';
                document.getElementById('risk-severity').className = 'inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-500 uppercase tracking-tighter';
            }
        } else {
            messageEl.textContent = "No active threats detected";
            detailsEl.classList.add('hidden');
            cardEl.className = 'glass-card p-6 border-l-4 border-l-emerald-500';
            iconEl.className = 'fas fa-circle-check text-emerald-400';
        }
    }

    function updateMetricsUI(data) {
        if (!data || data.length === 0) return;

        // Take last 20 for charts
        const reversed = [...data].reverse();
        
        cpuHistory = reversed.map(m => m.cpu);
        memHistory = reversed.map(m => m.memory);
        errorHistory = reversed.map(m => m.error_rate * 10); // scale up for visibility

        mainChart.data.labels = Array(cpuHistory.length).fill('');
        mainChart.data.datasets[0].data = cpuHistory;
        mainChart.data.datasets[1].data = memHistory;
        mainChart.data.datasets[2].data = errorHistory;
        mainChart.update('none');

        // Update card values (latest)
        const latest = data[0];
        document.getElementById('cpu-value').textContent = Math.round(latest.cpu);
        document.getElementById('memory-value').textContent = Math.round(latest.memory);
        document.getElementById('disk-value').textContent = Math.round(latest.disk) + '%';
        document.getElementById('latency-value').textContent = Math.round(latest.response_time) + ' ms';
        
        document.getElementById('disk-bar').style.width = latest.disk + '%';
        document.getElementById('latency-bar').style.width = Math.min(100, latest.response_time / 5) + '%';

        // Update Sparks
        cpuSpark.data.datasets[0].data = cpuHistory.slice(-10);
        cpuSpark.update('none');
        memSpark.data.datasets[0].data = memHistory.slice(-10);
        memSpark.update('none');
    }

    function updateIncidentsUI(data) {
        const table = document.getElementById('incidents-table');
        if (!data || data.length === 0) {
            table.innerHTML = '<tr><td colspan="6" class="px-6 py-10 text-center text-slate-500 italic">No incidents recorded yet</td></tr>';
            return;
        }

        table.innerHTML = data.map(inc => `
            <tr class="hover:bg-white/5 transition-colors">
                <td class="px-6 py-4 font-mono text-xs text-slate-400">#${inc.id}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold ${getSeverityClass(inc.severity)}">
                        ${inc.severity}
                    </span>
                </td>
                <td class="px-6 py-4 text-slate-200 font-medium">${inc.root_cause || 'Undetermined'}</td>
                <td class="px-6 py-4 text-xs font-mono text-slate-400">${inc.created_at}</td>
                <td class="px-6 py-4">
                    <div class="flex items-center space-x-1">
                        <span class="w-1.5 h-1.5 rounded-full ${inc.status === 'OPEN' ? 'bg-rose-500 animate-pulse' : 'bg-slate-500'}"></span>
                        <span class="text-[10px] font-bold uppercase ${inc.status === 'OPEN' ? 'text-rose-400' : 'text-slate-500'}">${inc.status}</span>
                    </div>
                </td>
                <td class="px-6 py-4 text-right">
                    <button class="text-slate-500 hover:text-sky-400 transition-colors">
                        <i class="fas fa-arrow-right"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    function getSeverityClass(sev) {
        switch(sev) {
            case 'CRITICAL': return 'bg-rose-500/20 text-rose-500';
            case 'HIGH': return 'bg-orange-500/20 text-orange-500';
            case 'MEDIUM': return 'bg-amber-500/20 text-amber-500';
            default: return 'bg-sky-500/20 text-sky-500';
        }
    }

    // -------------------------------------------------------------------------
    // Utils
    // -------------------------------------------------------------------------
    function updateClock() {
        const now = new Date();
        document.getElementById('current-time').textContent = now.toLocaleTimeString('en-US', { hour12: false });
    }

    // -------------------------------------------------------------------------
    // Init
    // -------------------------------------------------------------------------
    setInterval(updateClock, 1000);
    setInterval(fetchData, REFRESH_INTERVAL);
    updateClock();
    fetchData();
});
