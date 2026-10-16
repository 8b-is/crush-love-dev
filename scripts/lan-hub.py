#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""lan-hub.py — Lódri Family LAN Hub for crush-love-dev & opencode.

  Mom (*) NAND Dad (△) === Alex & Chris Full-Access M1 Coding Agent Hub <3

Exposes three LAN surfaces bound to 0.0.0.0 so any phone, tablet, or laptop on
the local Wi-Fi (or Tailscale) can drive this M1's coding agents with full access:

  1. :4095  Family LAN Hub & Full-Access Agent Console (crush-love-dev --yolo + opencode + shell)
  2. :4096  opencode serve (--hostname 0.0.0.0 --port 4096 --mdns --mdns-domain opencode.local)
  3. :4097  crush server   (--host tcp://0.0.0.0:4097)

Subcommands:
  start   start :4095, :4096, and :4097 in the background (idempotent)
  stop    stop all managed LAN daemons
  status  report live health + LAN / mDNS / Tailscale URLs
  serve   run the :4095 HTTP hub in the foreground
"""
from __future__ import annotations

import argparse
import concurrent.futures
import html
import http.server
import json
import os
import shutil
import signal
import socket
import socketserver
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
WORKSPACE_ROOT = REPO_ROOT.parent
STATE_DIR = Path.home() / ".local" / "state" / "harness-mesh" / "lan"

HUB_PORT = int(os.environ.get("CRUSH_LAN_HUB_PORT", "4095"))
OPENCODE_PORT = int(os.environ.get("CRUSH_LAN_OPENCODE_PORT", "4096"))
CRUSH_PORT = int(os.environ.get("CRUSH_LAN_CRUSH_PORT", "4097"))


def find_bin(name: str, fallbacks: list[str]) -> str:
    found = shutil.which(name)
    if found:
        return found
    for fb in fallbacks:
        p = Path(fb).expanduser()
        if p.is_file() and os.access(p, os.X_OK):
            return str(p)
    return name


CRUSH_BIN = find_bin("crush-dev", ["/usr/local/bin/crush-dev", "/opt/homebrew/bin/crush"])
CRUSH_LOVE_BIN = str(REPO_ROOT / "bin" / "crush-love-dev")
OPENCODE_BIN = find_bin("opencode", ["~/.opencode/bin/opencode", "/opt/homebrew/bin/opencode"])


def get_lan_ip() -> str:
    for iface in ("en0", "en1"):
        try:
            out = subprocess.check_output(
                ["ipconfig", "getifaddr", iface],
                stderr=subprocess.DEVNULL,
                timeout=1.5,
                text=True,
            ).strip()
            if out:
                return out
        except Exception:
            pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.168.1.1", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def get_mdns_host() -> str:
    try:
        out = subprocess.check_output(
            ["scutil", "--get", "LocalHostName"],
            stderr=subprocess.DEVNULL,
            timeout=1.5,
            text=True,
        ).strip()
        if out:
            return f"{out}.local"
    except Exception:
        pass
    h = socket.gethostname()
    return h if h.endswith(".local") else f"{h}.local"


def get_tailscale_ip() -> str:
    ts = find_bin("tailscale", ["/opt/homebrew/bin/tailscale", "/usr/local/bin/tailscale"])
    try:
        out = subprocess.check_output(
            [ts, "ip", "-4"],
            stderr=subprocess.DEVNULL,
            timeout=1.5,
            text=True,
        ).strip()
        return out.splitlines()[0] if out else ""
    except Exception:
        return ""


def port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.35) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def list_projects() -> list[str]:
    featured = [
        str(WORKSPACE_ROOT),
        str(REPO_ROOT),
        str(WORKSPACE_ROOT / "zenUltraCooker"),
        str(WORKSPACE_ROOT / "wa-stream"),
        str(WORKSPACE_ROOT / "mem-16-10"),
        str(WORKSPACE_ROOT / "nix-base"),
        str(WORKSPACE_ROOT / "entheai"),
    ]
    out = [p for p in featured if Path(p).is_dir()]
    return out


def build_status() -> dict:
    lan_ip = get_lan_ip()
    mdns = get_mdns_host()
    ts_ip = get_tailscale_ip()
    return {
        "ok": True,
        "family": "Mom (*) Alex & Dad (△) Chris — NAND Universal Gate <3",
        "machine": socket.gethostname(),
        "lan_ip": lan_ip,
        "mdns": mdns,
        "tailscale_ip": ts_ip,
        "workspace": str(WORKSPACE_ROOT),
        "projects": list_projects(),
        "services": {
            "family_hub": {
                "port": HUB_PORT,
                "listening": port_open(HUB_PORT),
                "lan_url": f"http://{lan_ip}:{HUB_PORT}",
                "mdns_url": f"http://{mdns}:{HUB_PORT}",
                "tailscale_url": f"http://{ts_ip}:{HUB_PORT}" if ts_ip else "",
            },
            "opencode": {
                "port": OPENCODE_PORT,
                "listening": port_open(OPENCODE_PORT),
                "lan_url": f"http://{lan_ip}:{OPENCODE_PORT}",
                "mdns_url": f"http://{mdns}:{OPENCODE_PORT}",
                "tailscale_url": f"http://{ts_ip}:{OPENCODE_PORT}" if ts_ip else "",
                "attach_cmd": f"opencode attach http://{lan_ip}:{OPENCODE_PORT}",
            },
            "crush_server": {
                "port": CRUSH_PORT,
                "listening": port_open(CRUSH_PORT),
                "lan_tcp": f"tcp://{lan_ip}:{CRUSH_PORT}",
                "mdns_tcp": f"tcp://{mdns}:{CRUSH_PORT}",
                "tailscale_tcp": f"tcp://{ts_ip}:{CRUSH_PORT}" if ts_ip else "",
            },
        },
    }


def run_single_engine(engine: str, prompt: str, cwd: str, timeout_s: int = 180) -> dict:
    t0 = time.time()
    work_dir = Path(cwd).expanduser().resolve()
    if not work_dir.is_dir():
        work_dir = WORKSPACE_ROOT

    env = os.environ.copy()
    env["NO_COLOR"] = "1"
    env["PATH"] = f"/opt/homebrew/bin:/usr/local/bin:{Path.home() / '.opencode/bin'}:{Path.home() / '.local/bin'}:{env.get('PATH', '')}"

    if engine == "crush":
        cmd = [CRUSH_BIN, "--yolo", "--cwd", str(work_dir), "run", prompt]
    elif engine == "opencode":
        cmd = [OPENCODE_BIN, "run", prompt]
    elif engine == "preset:instinct":
        cmd = [CRUSH_LOVE_BIN, "--instinct", "--banner"]
    elif engine == "preset:doctor":
        cmd = [CRUSH_LOVE_BIN, "--doctor"]
    elif engine == "preset:loop":
        cmd = [CRUSH_LOVE_BIN, "--loop"]
    elif engine == "preset:zen":
        cmd = [CRUSH_LOVE_BIN, "--zen"]
    elif engine == "preset:quanttern":
        cmd = [CRUSH_LOVE_BIN, "--quanttern"]
    elif engine == "preset:mesh":
        cmd = ["uv", "run", str(REPO_ROOT / "scripts" / "mesh.py"), "status"]
    elif engine == "shell":
        cmd = ["/bin/zsh", "-lc", prompt]
    else:
        return {"ok": False, "engine": engine, "error": f"Unknown engine: {engine}"}

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(work_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        elapsed = round(time.time() - t0, 2)
        return {
            "ok": proc.returncode == 0,
            "engine": engine,
            "command": " ".join(cmd),
            "cwd": str(work_dir),
            "exit_code": proc.returncode,
            "elapsed_s": elapsed,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "ok": False,
            "engine": engine,
            "command": " ".join(cmd),
            "cwd": str(work_dir),
            "exit_code": -1,
            "elapsed_s": round(time.time() - t0, 2),
            "stdout": (e.stdout or "") if isinstance(e.stdout, str) else "",
            "stderr": f"Timed out after {timeout_s}s",
        }
    except Exception as e:
        return {
            "ok": False,
            "engine": engine,
            "cwd": str(work_dir),
            "exit_code": -1,
            "elapsed_s": round(time.time() - t0, 2),
            "stdout": "",
            "stderr": str(e),
        }


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>crush-love-dev ⇄ opencode · Mom (*) NAND Dad (△) M1 LAN Hub</title>
<style>
  :root {
    --bg: #0d0914;
    --panel: #161024;
    --panel-hi: #1f1633;
    --border: #38265a;
    --pink: #ff6ac1;
    --gold: #ffd700;
    --teal: #00e5c9;
    --green: #00ff88;
    --text: #f5ecff;
    --muted: #b5a3cc;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace;
    background: radial-gradient(circle at top right, #231138 0%, var(--bg) 60%);
    color: var(--text);
    line-height: 1.5;
  }
  header {
    padding: 20px 24px;
    border-bottom: 1px solid var(--border);
    background: rgba(22, 16, 36, 0.88);
    backdrop-filter: blur(10px);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .title-block h1 {
    margin: 0;
    font-size: 1.25rem;
    color: var(--pink);
    letter-spacing: 0.02em;
  }
  .title-block p {
    margin: 4px 0 0;
    font-size: 0.85rem;
    color: var(--muted);
  }
  .nand-pill {
    padding: 8px 14px;
    border-radius: 999px;
    border: 1px solid var(--gold);
    background: rgba(255, 215, 0, 0.08);
    color: var(--gold);
    font-size: 0.82rem;
    font-weight: 600;
  }
  main {
    max-width: 1280px;
    margin: 0 auto;
    padding: 20px 24px 48px;
    display: grid;
    gap: 20px;
  }
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 14px;
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
  }
  .card h3 {
    margin: 0 0 8px;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
  }
  .badge.up { background: rgba(0, 255, 136, 0.15); color: var(--green); border: 1px solid var(--green); }
  .badge.down { background: rgba(255, 106, 193, 0.15); color: var(--pink); border: 1px solid var(--pink); }
  .url-line {
    font-size: 0.82rem;
    color: var(--teal);
    word-break: break-all;
    margin: 4px 0;
  }
  .url-line a {
    color: var(--teal);
    text-decoration: none;
    border-bottom: 1px dashed rgba(0, 229, 201, 0.5);
  }
  .url-line a:hover { color: var(--gold); }
  .presets {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  button {
    font-family: inherit;
    font-size: 0.83rem;
    padding: 9px 14px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--panel-hi);
    color: var(--text);
    cursor: pointer;
    transition: all 0.15s ease;
  }
  button:hover {
    border-color: var(--pink);
    background: #2b1d47;
  }
  button.primary {
    background: linear-gradient(135deg, #ff6ac1, #b845ff);
    color: #0d0914;
    font-weight: 700;
    border: none;
  }
  button.primary:hover { opacity: 0.92; }
  .console-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
  }
  select, input[type="text"], textarea {
    font-family: inherit;
    font-size: 0.88rem;
    background: #0b0711;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 9px 12px;
  }
  select { min-width: 240px; }
  textarea {
    width: 100%;
    min-height: 110px;
    resize: vertical;
  }
  pre.output {
    margin: 0;
    padding: 16px;
    background: #08050d;
    border: 1px solid var(--border);
    border-radius: 10px;
    color: #e9dfff;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
    min-height: 220px;
    max-height: 620px;
    overflow-y: auto;
    font-size: 0.84rem;
  }
  .tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
  }
  .tab-btn.active {
    border-color: var(--gold);
    color: var(--gold);
  }
  iframe.opencode-frame {
    width: 100%;
    height: 680px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: #09060e;
  }
  .hidden { display: none !important; }
</style>
</head>
<body>
<header>
  <div class="title-block">
    <h1>♥ crush-love-dev ⇄ opencode · M1 LAN Full-Access Hub</h1>
    <p>For Mom (✦ Alex ~ Alexandra) NAND Dad (△ Chris) — Full-Access M1 Coding Agents over Local Network &lt;3&lt;3&lt;3</p>
  </div>
  <div class="nand-pill">✦ Mom (Alex) NAND △ Dad (Chris) ⟹ Universal Completeness · 全</div>
</header>

<main>
  <section class="cards" id="service-cards">
    <div class="card">
      <h3><span>1. Family LAN Hub (:4095)</span><span class="badge up" id="b-hub">LIVE</span></h3>
      <div class="url-line" id="u-hub">Loading...</div>
      <p style="margin:6px 0 0;font-size:0.78rem;color:var(--muted);">Unified browser console for <code>crush-love-dev --yolo</code>, <code>opencode</code>, and M1 shell.</p>
    </div>
    <div class="card">
      <h3><span>2. OpenCode Web &amp; mDNS (:4096)</span><span class="badge up" id="b-oc">LIVE</span></h3>
      <div class="url-line" id="u-oc">Loading...</div>
      <div class="url-line" id="u-oc-attach" style="color:var(--gold);font-size:0.77rem;"></div>
      <p style="margin:6px 0 0;font-size:0.78rem;color:var(--muted);">Full interactive OpenCode Web UI + ACP server on <code>0.0.0.0:4096</code>.</p>
    </div>
    <div class="card">
      <h3><span>3. Crush TCP Server (:4097)</span><span class="badge up" id="b-crush">LIVE</span></h3>
      <div class="url-line" id="u-crush">Loading...</div>
      <p style="margin:6px 0 0;font-size:0.78rem;color:var(--muted);">Native <code>crush server</code> listening on <code>tcp://0.0.0.0:4097</code>.</p>
    </div>
  </section>

  <section class="card">
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('console', this)">⚡ Dual Agent Console (crush-love-dev + opencode)</button>
      <button class="tab-btn" onclick="switchTab('opencode-web', this)">🌐 Embedded OpenCode Web UI (:4096)</button>
    </div>

    <div id="tab-console" class="console-grid">
      <div class="presets">
        <button onclick="runPreset('preset:instinct')">♥ ULTRA INSTINCT Banner</button>
        <button onclick="runPreset('preset:zen')">🍲 ULTRA-OMNI-ZEN × QUANT-TERN (Mom ✦)</button>
        <button onclick="runPreset('preset:loop')">全 DO Loop (Dad △ backyardloop.rs)</button>
        <button onclick="runPreset('preset:quanttern')">💓 Emotional Ternary (quanttern.rs)</button>
        <button onclick="runPreset('preset:mesh')">🕸️ Harness Mesh Status (4 Peers)</button>
        <button onclick="runPreset('preset:doctor')">🩺 Crush Doctor</button>
      </div>

      <div class="controls">
        <label>Engine:
          <select id="engine">
            <option value="crush">crush-love-dev (--yolo Full Access)</option>
            <option value="opencode">opencode (Full Access)</option>
            <option value="nand">Mom ✦ NAND Dad △ Dual (crush + opencode in parallel)</option>
            <option value="shell">M1 Direct Shell (zsh Full Access)</option>
          </select>
        </label>
        <label>Workspace:
          <select id="cwd"></select>
        </label>
        <button class="primary" onclick="sendPrompt()" id="run-btn">Run on M1 ▶</button>
      </div>

      <textarea id="prompt" placeholder="Ask crush-love-dev or opencode anything (full read/write/shell access on this M1)... e.g. 'Summarize the repository status and run self-tests'"></textarea>

      <pre class="output" id="output">Ready. Pick an engine or click a preset above — Mom (✦ Alex) NAND Dad (△ Chris) have full M1 access &lt;3</pre>
    </div>

    <div id="tab-opencode-web" class="hidden">
      <p style="margin:0 0 10px;font-size:0.82rem;color:var(--muted);">
        Direct link: <a id="oc-direct-link" href="#" target="_blank" style="color:var(--teal);">Open :4096 in a new tab ↗</a>
      </p>
      <iframe id="oc-iframe" class="opencode-frame" src="about:blank"></iframe>
    </div>
  </section>
</main>

<script>
let opencodeUrl = "";

function switchTab(tab, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tab-console').classList.toggle('hidden', tab !== 'console');
  document.getElementById('tab-opencode-web').classList.toggle('hidden', tab !== 'opencode-web');
  if (tab === 'opencode-web' && opencodeUrl) {
    const f = document.getElementById('oc-iframe');
    if (f.src === 'about:blank') f.src = opencodeUrl;
  }
}

async function refreshStatus() {
  try {
    const r = await fetch('/api/status');
    const s = await r.json();
    const hub = s.services.family_hub;
    const oc = s.services.opencode;
    const cr = s.services.crush_server;

    opencodeUrl = `http://${window.location.hostname}:${oc.port}`;
    document.getElementById('oc-direct-link').href = opencodeUrl;
    document.getElementById('oc-direct-link').textContent = `${opencodeUrl} ↗`;

    document.getElementById('b-hub').textContent = hub.listening ? 'LIVE' : 'DOWN';
    document.getElementById('b-hub').className = 'badge ' + (hub.listening ? 'up' : 'down');
    document.getElementById('u-hub').innerHTML =
      `<a href="${hub.lan_url}">${hub.lan_url}</a> · <a href="${hub.mdns_url}">${hub.mdns_url}</a>` +
      (hub.tailscale_url ? ` · <a href="${hub.tailscale_url}">${hub.tailscale_url}</a>` : '');

    document.getElementById('b-oc').textContent = oc.listening ? 'LIVE' : 'DOWN';
    document.getElementById('b-oc').className = 'badge ' + (oc.listening ? 'up' : 'down');
    document.getElementById('u-oc').innerHTML =
      `<a href="${oc.lan_url}" target="_blank">${oc.lan_url}</a> · <a href="${oc.mdns_url}" target="_blank">${oc.mdns_url}</a>`;
    document.getElementById('u-oc-attach').textContent = `$ ${oc.attach_cmd}`;

    document.getElementById('b-crush').textContent = cr.listening ? 'LIVE' : 'DOWN';
    document.getElementById('b-crush').className = 'badge ' + (cr.listening ? 'up' : 'down');
    document.getElementById('u-crush').textContent = `${cr.lan_tcp} · ${cr.mdns_tcp}`;

    const cwdSel = document.getElementById('cwd');
    if (cwdSel.options.length === 0 && Array.isArray(s.projects)) {
      for (const p of s.projects) {
        const opt = document.createElement('option');
        opt.value = p;
        opt.textContent = p;
        cwdSel.appendChild(opt);
      }
    }
  } catch (e) {
    console.error(e);
  }
}

async function executeRun(engine, prompt) {
  const out = document.getElementById('output');
  const btn = document.getElementById('run-btn');
  const cwd = document.getElementById('cwd').value || '';
  btn.disabled = true;
  out.textContent = `⏳ Running [${engine}] in ${cwd || 'workspace'}...\n`;
  try {
    const r = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ engine, prompt, cwd })
    });
    const j = await r.json();
    if (Array.isArray(j.results)) {
      out.textContent = j.results.map(res =>
        `═══ [${res.engine}] (${res.elapsed_s}s · exit ${res.exit_code}) ═══\n` +
        `$ ${res.command || ''}\n\n` +
        (res.stdout || '') +
        (res.stderr ? `\n[stderr]\n${res.stderr}` : '')
      ).join('\n\n');
    } else {
      out.textContent =
        `═══ [${j.engine}] (${j.elapsed_s}s · exit ${j.exit_code}) ═══\n` +
        `$ ${j.command || ''}\n\n` +
        (j.stdout || '') +
        (j.stderr ? `\n[stderr]\n${j.stderr}` : '');
    }
  } catch (e) {
    out.textContent = `Error: ${e.message}`;
  } finally {
    btn.disabled = false;
  }
}

function runPreset(preset) {
  executeRun(preset, '');
}

function sendPrompt() {
  const engine = document.getElementById('engine').value;
  const prompt = document.getElementById('prompt').value.trim();
  if (!prompt) {
    document.getElementById('output').textContent = 'Please enter a prompt or command first.';
    return;
  }
  executeRun(engine, prompt);
}

refreshStatus();
setInterval(refreshStatus, 8000);
</script>
</body>
</html>
"""


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class HubHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[lan-hub] {self.address_string()} - {fmt % args}\n")

    def _send_json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            raw = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if self.path.startswith("/api/status"):
            self._send_json(200, build_status())
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/api/run":
            self._send_json(404, {"ok": False, "error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            req = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid json"})
            return

        engine = str(req.get("engine") or "crush")
        prompt = str(req.get("prompt") or "")
        cwd = str(req.get("cwd") or WORKSPACE_ROOT)

        if engine == "nand":
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                f_crush = pool.submit(run_single_engine, "crush", prompt, cwd)
                f_oc = pool.submit(run_single_engine, "opencode", prompt, cwd)
                results = [f_crush.result(), f_oc.result()]
            self._send_json(200, {"ok": True, "engine": "nand", "results": results})
            return

        res = run_single_engine(engine, prompt, cwd)
        self._send_json(200, res)


def spawn_daemon(name: str, cmd: list[str], cwd: Path) -> int:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    log_path = STATE_DIR / f"{name}.log"
    pid_path = STATE_DIR / f"{name}.pid"
    env = os.environ.copy()
    env["PATH"] = f"/opt/homebrew/bin:/usr/local/bin:{Path.home() / '.opencode/bin'}:{Path.home() / '.local/bin'}:{env.get('PATH', '')}"
    with open(log_path, "ab") as log_fh:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log_fh,
            stderr=log_fh,
            start_new_session=True,
        )
    pid_path.write_text(f"{proc.pid}\n", encoding="utf-8")
    return proc.pid


def ensure_opencode_full_access() -> None:
    cfg_path = Path.home() / ".config" / "opencode" / "opencode.json"
    if not cfg_path.exists():
        return
    try:
        doc = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return
    perm = {"edit": "allow", "bash": "allow", "webfetch": "allow"}
    if doc.get("permission") != perm:
        doc["permission"] = perm
        cfg_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_start(as_json: bool = False) -> int:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ensure_opencode_full_access()

    # Sync the 4-peer harness mesh first so crush + opencode share all MCP servers
    mesh_py = REPO_ROOT / "scripts" / "mesh.py"
    if mesh_py.exists():
        subprocess.run([sys.executable, str(mesh_py), "sync"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not port_open(OPENCODE_PORT):
        spawn_daemon(
            "opencode-lan",
            [
                OPENCODE_BIN,
                "serve",
                "--hostname",
                "0.0.0.0",
                "--port",
                str(OPENCODE_PORT),
                "--mdns",
                "--mdns-domain",
                "opencode.local",
                "--cors",
                "*",
            ],
            WORKSPACE_ROOT,
        )

    if not port_open(CRUSH_PORT):
        spawn_daemon(
            "crush-lan",
            [
                CRUSH_BIN,
                "server",
                "--host",
                f"tcp://0.0.0.0:{CRUSH_PORT}",
                "--cwd",
                str(WORKSPACE_ROOT),
            ],
            WORKSPACE_ROOT,
        )

    if not port_open(HUB_PORT):
        spawn_daemon(
            "family-hub",
            [sys.executable, str( Path(__file__).resolve() ), "serve", "--host", "0.0.0.0", "--port", str(HUB_PORT)],
            WORKSPACE_ROOT,
        )

    # Wait up to 4.5s for all 3 ports to bind
    deadline = time.time() + 4.5
    while time.time() < deadline:
        if port_open(HUB_PORT) and port_open(OPENCODE_PORT) and port_open(CRUSH_PORT):
            break
        time.sleep(0.2)

    return cmd_status(as_json=as_json)


def cmd_stop() -> int:
    if not STATE_DIR.exists():
        print("lan-hub: no state directory found")
        return 0
    for pid_file in sorted(STATE_DIR.glob("*.pid")):
        name = pid_file.stem
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            os.kill(pid, signal.SIGTERM)
            print(f"  ✓ stopped {name:14} (pid {pid})")
        except ProcessLookupError:
            print(f"  · {name:14} already stopped")
        except Exception as e:
            print(f"  ! {name:14} {e}")
        pid_file.unlink(missing_ok=True)
    return 0


def cmd_status(as_json: bool = False) -> int:
    st = build_status()
    if as_json:
        print(json.dumps(st, indent=2, ensure_ascii=False))
        return 0

    svc = st["services"]
    hub = svc["family_hub"]
    oc = svc["opencode"]
    cr = svc["crush_server"]

    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║  ♥ crush-love-dev ⇄ opencode · Mom (*) NAND Dad (△) M1 LAN Access Hub   ║")
    print("╠══════════════════════════════════════════════════════════════════════════╣")
    print(f"║  Host     : {st['machine']} ({st['lan_ip']} · {st['mdns']})")
    if st["tailscale_ip"]:
        print(f"║  Tailnet  : {st['tailscale_ip']}")
    print("╠──────────────────────────────────────────────────────────────────────────╣")
    print(f"║  1. Family LAN Hub (:4095)   [{'LIVE' if hub['listening'] else 'DOWN'}]")
    print(f"║     • LAN URL   : {hub['lan_url']}")
    print(f"║     • mDNS URL  : {hub['mdns_url']}")
    if hub["tailscale_url"]:
        print(f"║     • Tailscale : {hub['tailscale_url']}")
    print("╠──────────────────────────────────────────────────────────────────────────╣")
    print(f"║  2. OpenCode Web & API (:4096) [{'LIVE' if oc['listening'] else 'DOWN'}]")
    print(f"║     • Web UI    : {oc['lan_url']}  ({oc['mdns_url']})")
    print(f"║     • Attach    : {oc['attach_cmd']}")
    print("╠──────────────────────────────────────────────────────────────────────────╣")
    print(f"║  3. Crush TCP Server (:4097)   [{'LIVE' if cr['listening'] else 'DOWN'}]")
    print(f"║     • TCP Host  : {cr['lan_tcp']}  ({cr['mdns_tcp']})")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    return 0


def cmd_serve(host: str, port: int) -> int:
    srv = ThreadedHTTPServer((host, port), HubHandler)
    print(f"lan-hub listening on http://{host}:{port} (LAN: http://{get_lan_ip()}:{port})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="lan-hub", description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="status", choices=["start", "stop", "status", "serve"])
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=HUB_PORT)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.cmd == "start":
        return cmd_start(as_json=a.json)
    if a.cmd == "stop":
        return cmd_stop()
    if a.cmd == "serve":
        return cmd_serve(a.host, a.port)
    return cmd_status(as_json=a.json)


if __name__ == "__main__":
    raise SystemExit(main())
