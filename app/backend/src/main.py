"""
FinShield - Secure Financial Transaction API
DevSecOps SDLC Pipeline | Finance Domain
"""

import logging
import json
import uuid
import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from routes.transactions import router as transactions_router
from utils.logger import get_structured_logger

logger = get_structured_logger("finshield.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FinShield API starting up", extra={"event": "startup", "version": os.getenv("APP_VERSION", "1.0.0")})
    yield
    logger.info("FinShield API shutting down", extra={"event": "shutdown"})

app = FastAPI(
    title="FinShield API",
    description="Secure Financial Transaction Processing — DevSecOps Pipeline",
    version=os.getenv("APP_VERSION", "1.0.0"),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start).total_seconds() * 1000
    logger.info(
        "HTTP request processed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration, 2),
            "client_ip": request.client.host if request.client else "unknown",
        }
    )
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(transactions_router, prefix="/api/v1/transactions", tags=["Transactions"])

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "finshield-api",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>FinShield — Secure Transaction Dashboard</title>
  <style>
    :root {
      --bg: #0a0e1a;
      --surface: #111827;
      --surface2: #1a2235;
      --border: #1e2d45;
      --accent: #00d4aa;
      --accent2: #3b82f6;
      --accent3: #f59e0b;
      --danger: #ef4444;
      --text: #e2e8f0;
      --muted: #64748b;
      --success: #22c55e;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }
    .topbar { background: var(--surface); border-bottom: 1px solid var(--border); padding: 0 2rem; display: flex; align-items: center; justify-content: space-between; height: 64px; position: sticky; top: 0; z-index: 10; }
    .logo { display: flex; align-items: center; gap: 10px; }
    .logo-icon { width: 36px; height: 36px; background: linear-gradient(135deg, var(--accent), var(--accent2)); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    .logo-text { font-size: 1.2rem; font-weight: 700; letter-spacing: -0.5px; }
    .logo-text span { color: var(--accent); }
    .badge { background: rgba(0,212,170,0.15); color: var(--accent); border: 1px solid rgba(0,212,170,0.3); padding: 3px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
    .main { max-width: 1280px; margin: 0 auto; padding: 2rem; }
    .page-title { font-size: 1.6rem; font-weight: 700; margin-bottom: 0.3rem; }
    .page-sub { color: var(--muted); font-size: 0.9rem; margin-bottom: 2rem; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.2rem 1.5rem; position: relative; overflow: hidden; }
    .stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
    .stat-card.green::before { background: var(--success); }
    .stat-card.blue::before { background: var(--accent2); }
    .stat-card.yellow::before { background: var(--accent3); }
    .stat-card.red::before { background: var(--danger); }
    .stat-label { font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }
    .stat-value { font-size: 1.8rem; font-weight: 800; }
    .stat-sub { font-size: 0.78rem; color: var(--muted); margin-top: 0.3rem; }
    .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }
    @media(max-width:768px){ .grid2 { grid-template-columns: 1fr; } }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }
    .card-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 8px; }
    .card-title .dot { width: 8px; height: 8px; border-radius: 50%; }
    .dot-green { background: var(--success); box-shadow: 0 0 8px var(--success); }
    .dot-blue { background: var(--accent2); }
    .dot-yellow { background: var(--accent3); }
    .form-group { margin-bottom: 1rem; }
    label { display: block; font-size: 0.8rem; color: var(--muted); margin-bottom: 0.4rem; }
    input, select { width: 100%; background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 0.6rem 0.9rem; border-radius: 8px; font-size: 0.9rem; outline: none; transition: border 0.2s; }
    input:focus, select:focus { border-color: var(--accent); }
    .btn { width: 100%; padding: 0.75rem; background: linear-gradient(135deg, var(--accent), #00a884); color: #000; font-weight: 700; border: none; border-radius: 8px; cursor: pointer; font-size: 0.95rem; transition: opacity 0.2s; margin-top: 0.5rem; }
    .btn:hover { opacity: 0.85; }
    .btn:disabled { opacity: 0.4; cursor: not-allowed; }
    .tx-list { max-height: 340px; overflow-y: auto; }
    .tx-item { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--border); }
    .tx-item:last-child { border-bottom: none; }
    .tx-left { display: flex; align-items: center; gap: 10px; }
    .tx-icon { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }
    .tx-icon.send { background: rgba(239,68,68,0.15); }
    .tx-icon.receive { background: rgba(34,197,94,0.15); }
    .tx-icon.fraud { background: rgba(245,158,11,0.15); }
    .tx-id { font-size: 0.8rem; font-weight: 600; }
    .tx-time { font-size: 0.72rem; color: var(--muted); }
    .tx-amount { font-weight: 700; font-size: 0.95rem; }
    .tx-amount.neg { color: var(--danger); }
    .tx-amount.pos { color: var(--success); }
    .chip { padding: 2px 8px; border-radius: 999px; font-size: 0.68rem; font-weight: 700; }
    .chip-green { background: rgba(34,197,94,0.15); color: var(--success); }
    .chip-red { background: rgba(239,68,68,0.15); color: var(--danger); }
    .chip-yellow { background: rgba(245,158,11,0.15); color: var(--accent3); }
    .pipeline { display: flex; align-items: center; gap: 0; margin: 0.5rem 0 1.2rem; }
    .pipe-step { flex: 1; text-align: center; }
    .pipe-dot { width: 28px; height: 28px; border-radius: 50%; margin: 0 auto 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; }
    .pipe-active { background: var(--success); color: #000; box-shadow: 0 0 12px var(--success); }
    .pipe-wait { background: var(--border); color: var(--muted); }
    .pipe-line { flex: 1; height: 2px; background: var(--border); margin-bottom: 20px; }
    .pipe-line.active { background: var(--success); }
    .pipe-label { font-size: 0.65rem; color: var(--muted); }
    .alert-box { background: rgba(0,212,170,0.08); border: 1px solid rgba(0,212,170,0.2); border-radius: 8px; padding: 0.8rem 1rem; margin-top: 0.8rem; font-size: 0.85rem; display: none; }
    .alert-box.show { display: block; }
    .alert-err { background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.3); color: #fca5a5; }
    .footer { text-align: center; color: var(--muted); font-size: 0.78rem; margin-top: 3rem; padding-bottom: 2rem; }
    .pulse { animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
    .scrollbar-hide::-webkit-scrollbar { width: 4px; } 
    .scrollbar-hide::-webkit-scrollbar-track { background: transparent; }
    .scrollbar-hide::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
  </style>
</head>
<body>

<div class="topbar">
  <div class="logo">
    <div class="logo-icon">🛡</div>
    <div class="logo-text">Fin<span>Shield</span></div>
  </div>
  <div style="display:flex;gap:10px;align-items:center">
    <span class="badge">🔴 LIVE</span>
    <span class="badge" style="background:rgba(59,130,246,0.15);color:#60a5fa;border-color:rgba(59,130,246,0.3)">DevSecOps</span>
  </div>
</div>

<div class="main">
  <div class="page-title">Transaction Command Center</div>
  <div class="page-sub">Secure · Monitored · Automated via Jenkins + Vault + ELK + Kubernetes</div>

  <div class="stats-grid">
    <div class="stat-card green">
      <div class="stat-label">Total Transactions</div>
      <div class="stat-value" id="statTotal">0</div>
      <div class="stat-sub">↑ since session start</div>
    </div>
    <div class="stat-card blue">
      <div class="stat-label">Total Volume</div>
      <div class="stat-value" id="statVolume">$0</div>
      <div class="stat-sub">processed today</div>
    </div>
    <div class="stat-card yellow">
      <div class="stat-label">Fraud Flagged</div>
      <div class="stat-value" id="statFraud">0</div>
      <div class="stat-sub">suspicious detections</div>
    </div>
    <div class="stat-card" style="border-top: 3px solid var(--accent);">
      <div class="stat-label">API Status</div>
      <div class="stat-value" style="font-size:1.1rem;color:var(--success)" id="statHealth">● Online</div>
      <div class="stat-sub" id="statVersion">v1.0.0</div>
    </div>
  </div>

  <div class="grid2">
    <!-- Send Transaction -->
    <div class="card">
      <div class="card-title"><span class="dot dot-green"></span>New Transaction</div>
      <div class="form-group">
        <label>Sender Account</label>
        <input id="sender" placeholder="ACC-001234" value="ACC-001234"/>
      </div>
      <div class="form-group">
        <label>Receiver Account</label>
        <input id="receiver" placeholder="ACC-005678" value="ACC-005678"/>
      </div>
      <div class="form-group">
        <label>Amount (USD)</label>
        <input id="amount" type="number" placeholder="500.00" value="500"/>
      </div>
      <div class="form-group">
        <label>Transaction Type</label>
        <select id="txtype">
          <option value="transfer">Transfer</option>
          <option value="payment">Payment</option>
          <option value="withdrawal">Withdrawal</option>
          <option value="deposit">Deposit</option>
        </select>
      </div>
      <button class="btn" id="sendBtn" onclick="sendTransaction()">⚡ Execute Transaction</button>
      <div class="alert-box" id="txAlert"></div>
    </div>

    <!-- DevOps Pipeline Status -->
    <div class="card">
      <div class="card-title"><span class="dot dot-blue"></span>DevSecOps Pipeline</div>
      <div class="pipeline">
        <div class="pipe-step">
          <div class="pipe-dot pipe-active">✓</div>
          <div class="pipe-label">Git Push</div>
        </div>
        <div class="pipe-line active"></div>
        <div class="pipe-step">
          <div class="pipe-dot pipe-active">✓</div>
          <div class="pipe-label">Jenkins Build</div>
        </div>
        <div class="pipe-line active"></div>
        <div class="pipe-step">
          <div class="pipe-dot pipe-active">✓</div>
          <div class="pipe-label">Docker Push</div>
        </div>
        <div class="pipe-line active"></div>
        <div class="pipe-step">
          <div class="pipe-dot pipe-active">✓</div>
          <div class="pipe-label">K8s Deploy</div>
        </div>
      </div>
      <div style="font-size:0.78rem;color:var(--muted);margin-bottom:1rem">Last build: <span style="color:var(--success)">SUCCESS</span> · #42 · 2m 14s</div>

      <div style="background:var(--surface2);border-radius:8px;padding:1rem;font-size:0.78rem;">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem"><span style="color:var(--muted)">Vault Status</span><span style="color:var(--success)">● Sealed Secrets Active</span></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem"><span style="color:var(--muted)">ELK Stack</span><span style="color:var(--success)">● Logs Streaming</span></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem"><span style="color:var(--muted)">K8s HPA</span><span style="color:var(--success)">● Auto-scaling Active</span></div>
        <div style="display:flex;justify-content:space-between"><span style="color:var(--muted)">Ansible</span><span style="color:var(--success)">● Config Applied</span></div>
      </div>
      <div style="margin-top:1rem">
        <button onclick="loadTransactions()" style="background:transparent;border:1px solid var(--border);color:var(--text);padding:0.5rem 1rem;border-radius:8px;cursor:pointer;font-size:0.82rem;width:100%">🔄 Refresh Transactions</button>
      </div>
    </div>
  </div>

  <!-- Transaction History -->
  <div class="card">
    <div class="card-title"><span class="dot dot-yellow"></span>Live Transaction Feed <span class="pulse" style="color:var(--success);margin-left:8px;font-size:0.75rem">● LIVE</span></div>
    <div class="tx-list scrollbar-hide" id="txList">
      <div style="text-align:center;color:var(--muted);padding:2rem;font-size:0.85rem">Loading transactions...</div>
    </div>
  </div>
</div>

<div class="footer">FinShield v1.0.0 · Built with FastAPI · Secured by Vault · Monitored by ELK · Scaled by Kubernetes<br>CSE 816 Final Project — DevSecOps Finance Domain</div>

<script>
let stats = { total: 0, volume: 0, fraud: 0 };

async function apiFetch(path, opts={}) {
  const r = await fetch('/api/v1/transactions' + path, { headers: {'Content-Type':'application/json'}, ...opts });
  return r.json();
}

async function sendTransaction() {
  const btn = document.getElementById('sendBtn');
  const alert = document.getElementById('txAlert');
  btn.disabled = true; btn.textContent = '⏳ Processing...';
  alert.className = 'alert-box'; alert.style.display = 'none';
  try {
    const body = {
      sender_account: document.getElementById('sender').value,
      receiver_account: document.getElementById('receiver').value,
      amount: parseFloat(document.getElementById('amount').value),
      transaction_type: document.getElementById('txtype').value,
    };
    const res = await apiFetch('/', { method: 'POST', body: JSON.stringify(body) });
    const isFraud = res.fraud_score > 0.7;
    alert.className = 'alert-box show' + (isFraud ? ' alert-err' : '');
    alert.textContent = isFraud
      ? `⚠️ Transaction flagged! Fraud score: ${(res.fraud_score*100).toFixed(0)}% — ID: ${res.transaction_id}`
      : `✅ Success! TX ID: ${res.transaction_id} · Fraud score: ${(res.fraud_score*100).toFixed(0)}%`;
    await loadTransactions();
  } catch(e) {
    alert.className = 'alert-box show alert-err';
    alert.textContent = '❌ Error: ' + e.message;
  }
  btn.disabled = false; btn.textContent = '⚡ Execute Transaction';
}

async function loadTransactions() {
  try {
    const data = await apiFetch('/');
    const list = document.getElementById('txList');
    if (!data.transactions || data.transactions.length === 0) {
      list.innerHTML = '<div style="text-align:center;color:var(--muted);padding:2rem;font-size:0.85rem">No transactions yet. Execute one above!</div>';
      return;
    }
    stats = { total: data.transactions.length, volume: 0, fraud: 0 };
    list.innerHTML = data.transactions.slice().reverse().map(tx => {
      stats.volume += tx.amount;
      if (tx.fraud_score > 0.7) stats.fraud++;
      const isFraud = tx.fraud_score > 0.7;
      const isReceive = tx.transaction_type === 'deposit';
      const icon = isFraud ? '⚠️' : isReceive ? '⬇️' : '⬆️';
      const iconClass = isFraud ? 'fraud' : isReceive ? 'receive' : 'send';
      const amtClass = isReceive ? 'pos' : 'neg';
      const statusChip = isFraud
        ? '<span class="chip chip-yellow">FLAGGED</span>'
        : '<span class="chip chip-green">CLEARED</span>';
      const time = new Date(tx.timestamp).toLocaleTimeString();
      return `<div class="tx-item">
        <div class="tx-left">
          <div class="tx-icon ${iconClass}">${icon}</div>
          <div><div class="tx-id">${tx.transaction_id.slice(0,16)}...</div>
          <div class="tx-time">${tx.transaction_type} · ${time}</div></div>
        </div>
        <div style="text-align:right">
          <div class="tx-amount ${amtClass}">$${tx.amount.toFixed(2)}</div>
          ${statusChip}
        </div>
      </div>`;
    }).join('');
    document.getElementById('statTotal').textContent = stats.total;
    document.getElementById('statVolume').textContent = '$' + stats.volume.toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});
    document.getElementById('statFraud').textContent = stats.fraud;
  } catch(e) { console.error(e); }
}

async function checkHealth() {
  try {
    const r = await fetch('/health');
    const d = await r.json();
    document.getElementById('statHealth').textContent = '● Online';
    document.getElementById('statVersion').textContent = 'v' + d.version;
  } catch { document.getElementById('statHealth').textContent = '● Degraded'; }
}

checkHealth();
loadTransactions();
setInterval(loadTransactions, 10000);
</script>
</body>
</html>"""
    return HTMLResponse(content=html)
