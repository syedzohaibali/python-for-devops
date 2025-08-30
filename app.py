from flask import Flask, jsonify, render_template_string
import psutil, platform, time

app = Flask(__name__)

PAGE = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>System Monitoring</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>
    :root{
      --bg: #0b1020; --card:#12182b; --text:#e8edf2; --muted:#9aa7b4; --accent:#66d9e8; --border:#1c2542;
    }
    html.light{
      --bg:#f6f8fb; --card:#ffffff; --text:#0f172a; --muted:#5c6b7a; --accent:#2563eb; --border:#e5e7eb;
    }
    * { box-sizing: border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font: 14px/1.5 system-ui, -apple-system, Segoe UI, Roboto, Arial; }
    header { padding:20px 24px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--border); position:sticky; top:0; background:var(--bg); z-index:1; }
    .title { font-size:20px; font-weight:700; letter-spacing:.3px; }
    .controls { display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
    .btn { padding:8px 12px; border:1px solid var(--border); background:var(--card); color:var(--text); border-radius:10px; cursor:pointer; transition:.2s; }
    .btn:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(0,0,0,.1); }
    .grid { display:grid; gap:18px; padding:18px; grid-template-columns: repeat(12, 1fr); }
    .card { grid-column: span 12; background:var(--card); border:1px solid var(--border); border-radius:16px; padding:16px; box-shadow: 0 10px 30px rgba(0,0,0,.15); }
    .row { display:grid; grid-template-columns: 1fr 1fr; gap:16px; }
    .kpis { display:flex; gap:12px; flex-wrap:wrap; }
    .kpi { background:transparent; border:1px dashed var(--border); padding:10px 12px; border-radius:12px; }
    .muted { color:var(--muted); }
    .chart { width:100%; height:300px; }
    .small { font-size:12px; }
    .slider { accent-color: var(--accent); }
    @media (max-width: 920px){ .row{ grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <div class="title">System Monitoring</div>
    <div class="controls">
      <span class="muted small">Refresh:</span>
      <input id="rate" class="slider" type="range" min="500" max="5000" step="100" value="1000" />
      <span id="rateLabel" class="small muted">1.0s</span>
      <button id="toggle" class="btn">⏸ Pause</button>
      <button id="theme" class="btn">🌙 Dark</button>
    </div>
  </header>

  <section class="grid">
    <div class="card">
      <div class="kpis">
        <div class="kpi"><span class="muted small">Hostname</span><div id="host"></div></div>
        <div class="kpi"><span class="muted small">OS</span><div id="os"></div></div>
        <div class="kpi"><span class="muted small">CPU Cores</span><div id="cores"></div></div>
        <div class="kpi"><span class="muted small">Uptime</span><div id="uptime"></div></div>
        <div class="kpi"><span class="muted small">Disk</span><div id="disk"></div></div>
      </div>
    </div>

    <div class="card">
      <div class="row">
        <div><div class="muted small">CPU Utilization</div><div id="cpuGauge" class="chart"></div></div>
        <div><div class="muted small">Memory Utilization</div><div id="memGauge" class="chart"></div></div>
      </div>
    </div>

    <div class="card">
      <div class="row">
        <div><div class="muted small">CPU History</div><div id="cpuLine" class="chart"></div></div>
        <div><div class="muted small">Memory History</div><div id="memLine" class="chart"></div></div>
      </div>
    </div>
  </section>

<script>
  // ----- theme -----
  const htmlTag = document.documentElement;
  const savedTheme = localStorage.getItem('theme') || 'dark';
  htmlTag.classList.toggle('light', savedTheme === 'light');
  const themeBtn = document.getElementById('theme');
  setThemeLabel();
  themeBtn.onclick = () => { 
    htmlTag.classList.toggle('light'); 
    localStorage.setItem('theme', htmlTag.classList.contains('light') ? 'light' : 'dark');
    setThemeLabel();
    // resize redrawing for charts on theme change
    setTimeout(() => charts.forEach(c => c.resize()), 50);
  };
  function setThemeLabel(){ themeBtn.textContent = htmlTag.classList.contains('light') ? '🌞 Light' : '🌙 Dark'; }

  // ----- charts -----
  const cpuGauge = echarts.init(document.getElementById('cpuGauge'));
  const memGauge = echarts.init(document.getElementById('memGauge'));
  const cpuLine  = echarts.init(document.getElementById('cpuLine'));
  const memLine  = echarts.init(document.getElementById('memLine'));
  const charts = [cpuGauge, memGauge, cpuLine, memLine];

  const gaugeTpl = (name, val)=>({
      series: [{
        type: 'gauge',
        startAngle: 180, endAngle: 0, min:0, max:100, radius:'100%',
        axisLine: { lineStyle: { width: 20, color: [
          [0.4, '#10b981'], [0.8, '#f59e0b'], [1, '#ef4444']
        ]}},
        splitLine: { show:false }, axisTick:{ show:false }, axisLabel:{ show:false },
        pointer: { icon: 'path://M2.5 0 L-2.5 0 L0 70 Z', length: '55%', width: 8, itemStyle: { color: '#ddd' } },
        detail: { valueAnimation: true, formatter: '{value}%', fontSize: 28, color: '#fff' },
        data: [{ value: val, name }]
      }]
  });

  const lineTpl = (label) => ({
    grid:{ top:20, left:36, right:16, bottom:24 },
    xAxis:{ type:'category', boundaryGap:false, axisLabel:{ show:false } },
    yAxis:{ type:'value', min:0, max:100, splitLine:{ lineStyle:{ opacity:.15 }}},
    tooltip:{ trigger:'axis' },
    series:[{
      name: label, type:'line', smooth:true, showSymbol:false,
      areaStyle:{ opacity:.25 }, lineStyle:{ width:2 },
      data:[]
    }]
  });

  cpuGauge.setOption(gaugeTpl('CPU', 0));
  memGauge.setOption(gaugeTpl('Memory', 0));
  cpuLine.setOption(lineTpl('CPU %'));
  memLine.setOption(lineTpl('Memory %'));

  const cpuData = [], memData = [], labels = [];
  const MAX_POINTS = 60;

  // ----- controls -----
  let period = 1000;
  const rate = document.getElementById('rate'), rateLabel = document.getElementById('rateLabel');
  const toggleBtn = document.getElementById('toggle');
  rate.oninput = ()=>{ period = +rate.value; rateLabel.textContent = (period/1000).toFixed(1) + 's'; restart(); };
  toggleBtn.onclick = ()=>{ running = !running; toggleBtn.textContent = running ? '⏸ Pause' : '▶ Resume'; restart(); };

  // ----- metrics fetch -----
  let timer = null, running = true;
  function restart(){ if (timer) clearInterval(timer); if (running) timer = setInterval(tick, period); }
  window.addEventListener('resize', ()=> charts.forEach(c=> c.resize()) );

  async function tick(){
    try{
      const res = await fetch('/metrics', { cache:'no-store' });
      const m = await res.json();

      // KPIs
      document.getElementById('host').textContent  = m.hostname;
      document.getElementById('os').textContent    = m.os;
      document.getElementById('cores').textContent = m.cores;
      document.getElementById('disk').textContent  = `${m.disk.toFixed(1)}% used`;
      document.getElementById('uptime').textContent = humanizeUptime(m.uptime);

      // Gauges
      cpuGauge.setOption({ series:[{ data:[{value: m.cpu}] }] });
      memGauge.setOption({ series:[{ data:[{value: m.memory}] }] });

      // History (keep last 60 points)
      labels.push(new Date(m.ts).toLocaleTimeString());
      cpuData.push(m.cpu); memData.push(m.memory);
      if (labels.length > MAX_POINTS){ labels.shift(); cpuData.shift(); memData.shift(); }

      cpuLine.setOption({ xAxis:{ data: labels }, series:[{ data: cpuData }] });
      memLine.setOption({ xAxis:{ data: labels }, series:[{ data: memData }] });
    }catch(e){ console.error(e); }
  }

  function humanizeUptime(sec){
    const d=Math.floor(sec/86400), h=Math.floor(sec%86400/3600), m=Math.floor(sec%3600/60);
    return (d?d+'d ':'') + (h?h+'h ':'') + m+'m';
  }

  // start
  tick(); restart();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(PAGE)

@app.route("/metrics")
def metrics():
    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    net = psutil.net_io_counters()
    uptime = int(time.time() - psutil.boot_time())
    return jsonify(
        ts=int(time.time() * 1000),
        cpu=cpu,
        memory=mem,
        disk=disk,
        net_in=net.bytes_recv,
        net_out=net.bytes_sent,
        uptime=uptime,
        hostname=platform.node(),
        os=platform.platform(),
        cores=psutil.cpu_count(logical=True),
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
