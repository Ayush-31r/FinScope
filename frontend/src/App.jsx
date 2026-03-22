import { useState, useRef } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const AGENTS = [
  { id: "news", label: "News Retrieval", tag: "01", tech: "DuckDuckGo Search", desc: "Scans live financial news, press releases, and market sentiment signals for the ticker.", color: "#C8922A" },
  { id: "rag",  label: "SEC Filing RAG", tag: "02", tech: "FAISS + EDGAR",      desc: "Retrieves and synthesizes relevant passages from 10-K and 10-Q filings via vector search.", color: "#4A90C4" },
  { id: "risk", label: "Risk Scoring",   tag: "03", tech: "yFinance + Groq",    desc: "Computes volatility metrics, beta, and generates an LLM-powered risk assessment.", color: "#7B6EA0" },
];

const QUICK = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL"];
const STACK = ["LangGraph", "Groq / Llama 3.3", "FAISS", "HuggingFace", "yFinance", "EDGAR"];

function parseBrief(brief) {
  if (!brief) return [];
  const re = /(\d+)\.\s+([^—\n]+?)\s+[—-]\s+([\s\S]*?)(?=\d+\.\s|\s*$)/g;
  const sections = [];
  let m;
  while ((m = re.exec(brief)) !== null)
    sections.push({ num: m[1], title: m[2].trim(), body: m[3].trim() });
  if (!sections.length)
    return brief.split(/\n\n+/).filter(Boolean).map((b, i) => ({ title: `Section ${i+1}`, body: b.trim() }));
  return sections;
}

const css = `
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{
  --bg:#0B0E14;--bg2:#10141C;--bg3:#161B26;
  --border:rgba(255,255,255,0.07);--border2:rgba(255,255,255,0.12);
  --gold:#C8922A;--gold2:#E8B04A;--gold-dim:rgba(200,146,42,0.15);
  --blue:#4A90C4;--purple:#7B6EA0;
  --text:#E8E4DC;--muted:#6B7280;--muted2:#9CA3AF;
  --serif:'Playfair Display',Georgia,serif;
  --mono:'IBM Plex Mono',monospace;
  --cond:'IBM Plex Sans Condensed',sans-serif;
}
html,body,#root{height:100%;background:var(--bg);color:var(--text);font-family:var(--cond);-webkit-font-smoothing:antialiased;}
body::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgba(200,146,42,0.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(200,146,42,0.04) 1px,transparent 1px),
    linear-gradient(rgba(255,255,255,0.02) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,0.02) 1px,transparent 1px);
  background-size:80px 80px,80px 80px,20px 20px,20px 20px;
}
.wrap{position:relative;z-index:1;max-width:960px;margin:0 auto;padding:48px 24px 80px;}

.hdr{border-bottom:1px solid var(--border);padding-bottom:28px;margin-bottom:40px;display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;}
.brand{font-family:var(--serif);font-size:clamp(36px,6vw,56px);font-weight:900;line-height:1;letter-spacing:-0.02em;}
.brand span{color:var(--gold);}
.tagline{font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:0.18em;text-transform:uppercase;margin-top:8px;}
.hdr-badge{font-family:var(--mono);font-size:10px;color:var(--gold);border:1px solid rgba(200,146,42,0.3);padding:4px 10px;letter-spacing:0.12em;text-transform:uppercase;white-space:nowrap;}

.modules-label{font-family:var(--mono);font-size:10px;letter-spacing:0.2em;color:var(--muted);text-transform:uppercase;margin-bottom:14px;}
.modules{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border);border:1px solid var(--border);margin-bottom:40px;}
@media(max-width:600px){.modules{grid-template-columns:1fr;}}
.module{background:var(--bg2);padding:20px;position:relative;overflow:hidden;transition:background 0.2s;}
.module:hover{background:var(--bg3);}
.module-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px;}
.module-tag{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:0.15em;}
.module-icon{width:28px;height:28px;border:1px solid;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:11px;font-weight:600;flex-shrink:0;}
.module-name{font-family:var(--cond);font-size:13px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:4px;}
.module-tech{font-family:var(--mono);font-size:10px;color:var(--muted);margin-bottom:10px;}
.module-desc{font-size:15px;color:var(--muted2);line-height:1.6;}
.module-status{font-family:var(--mono);font-size:10px;margin-top:10px;height:14px;letter-spacing:0.05em;}
.module-bar{position:absolute;bottom:0;left:0;height:2px;width:0;transition:width 0.8s ease;}
.module.running .module-bar{width:100%;animation:barPulse 1.4s ease-in-out infinite;}
.module.done .module-bar{width:100%;}
@keyframes barPulse{0%,100%{opacity:0.5;}50%{opacity:1;}}

.flow{display:flex;align-items:center;justify-content:center;margin-bottom:40px;overflow-x:auto;padding:4px 0;flex-wrap:nowrap;}
.flow-node{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;white-space:nowrap;padding:6px 14px;border:1px solid var(--border);background:var(--bg2);}
.flow-node.active{color:var(--gold);border-color:rgba(200,146,42,0.4);background:var(--gold-dim);}
.flow-arrow{font-size:10px;color:var(--muted);padding:0 4px;flex-shrink:0;}

.input-section{margin-bottom:40px;}
.input-box{border:1px solid var(--border2);background:var(--bg2);padding:24px;position:relative;}
.input-box::before{content:'>';position:absolute;left:24px;top:50%;transform:translateY(-50%);font-family:var(--mono);font-size:14px;color:var(--gold);pointer-events:none;}
.input-row{display:flex;gap:0;align-items:stretch;}
.ticker-wrap{flex:1;padding-left:20px;}
.ticker-in{width:100%;background:transparent;border:none;outline:none;font-family:var(--mono);font-size:28px;font-weight:600;color:var(--text);letter-spacing:0.08em;caret-color:var(--gold);padding:0;}
.ticker-in::placeholder{color:var(--muted);font-weight:400;font-size:20px;}
.ticker-in:disabled{opacity:0.4;cursor:not-allowed;}
.run-btn{background:var(--gold);border:none;color:#000;font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;padding:0 28px;cursor:pointer;transition:background 0.2s,transform 0.1s;flex-shrink:0;white-space:nowrap;}
.run-btn:hover:not(:disabled){background:var(--gold2);}
.run-btn:active:not(:disabled){transform:scale(0.98);}
.run-btn:disabled{opacity:0.4;cursor:not-allowed;}
.quick-row{display:flex;align-items:center;gap:8px;margin-top:14px;flex-wrap:wrap;}
.quick-lbl{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:0.15em;text-transform:uppercase;}
.chip{background:transparent;border:1px solid var(--border2);color:var(--muted2);font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:0.1em;padding:4px 12px;cursor:pointer;transition:all 0.15s;text-transform:uppercase;}
.chip:hover:not(:disabled){border-color:var(--gold);color:var(--gold);background:var(--gold-dim);}
.chip:disabled{opacity:0.3;cursor:not-allowed;}

.err{border:1px solid rgba(220,80,80,0.3);background:rgba(220,80,80,0.08);padding:14px 18px;font-family:var(--mono);font-size:12px;color:#E87070;margin-bottom:24px;}

.results{animation:fadeUp 0.4s ease both;}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px);}to{opacity:1;transform:translateY(0);}}
.results-hdr{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:12px;border-bottom:1px solid var(--border);padding-bottom:16px;margin-bottom:24px;}
.results-ticker{font-family:var(--serif);font-size:36px;font-weight:900;color:var(--gold);}
.results-meta{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;}
.sections{display:flex;flex-direction:column;gap:2px;}
.sec{border:1px solid var(--border);background:var(--bg2);}
.sec-hdr{display:flex;align-items:center;gap:14px;padding:14px 18px;cursor:pointer;user-select:none;transition:background 0.15s;}
.sec-hdr:hover{background:var(--bg3);}
.sec-num{font-family:var(--mono);font-size:10px;color:var(--gold);opacity:0.6;width:20px;flex-shrink:0;}
.sec-title{font-family:var(--cond);font-size:13px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;flex:1;}
.sec-chev{font-size:10px;color:var(--muted);transition:transform 0.2s;flex-shrink:0;}
.sec-chev.open{transform:rotate(90deg);}
.sec-body{padding:20px 24px 24px 24px;font-size:16px;color:var(--muted2);line-height:1.9;border-top:1px solid var(--border);white-space:pre-wrap;}
.raw-row{display:flex;justify-content:flex-end;margin-top:16px;}
.raw-btn{background:transparent;border:1px solid var(--border);color:var(--muted);font-family:var(--mono);font-size:10px;letter-spacing:0.12em;text-transform:uppercase;padding:6px 14px;cursor:pointer;transition:all 0.15s;}
.raw-btn:hover{border-color:var(--gold);color:var(--gold);}
.raw-pre{margin-top:12px;background:var(--bg3);border:1px solid var(--border);padding:18px;font-family:var(--mono);font-size:11px;color:var(--muted2);line-height:1.7;white-space:pre-wrap;word-break:break-word;max-height:480px;overflow-y:auto;}

.footer{margin-top:60px;padding-top:24px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}
.footer-brand{font-family:var(--serif);font-size:14px;font-weight:700;color:var(--muted);}
.stack-tags{display:flex;gap:6px;flex-wrap:wrap;}
.stack-tag{font-family:var(--mono);font-size:10px;color:var(--muted);border:1px solid var(--border);padding:3px 8px;letter-spacing:0.08em;}
`;

function Section({ idx, title, body }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="sec">
      <div className="sec-hdr" onClick={() => setOpen(o => !o)}>
        <span className="sec-num">0{idx + 1}</span>
        <span className="sec-title">{title}</span>
        <span className={`sec-chev ${open ? "open" : ""}`}>▶</span>
      </div>
      {open && <div className="sec-body">{body}</div>}
    </div>
  );
}

const FLOW_NODES = ["Input", "Orchestrator", "News · RAG · Risk", "Synthesizer", "Brief"];

export default function App() {
  const [ticker, setTicker] = useState("");
  const [phase, setPhase] = useState("idle");
  const [agentPhase, setAgentPhase] = useState({ news: "idle", rag: "idle", risk: "idle" });
  const [agentStatus, setAgentStatus] = useState({ news: "", rag: "", risk: "" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [showRaw, setShowRaw] = useState(false);
  const abort = useRef(null);

  const run = async (sym) => {
    const t = (sym ?? ticker).trim().toUpperCase();
    if (!t) return;
    setPhase("running"); setError(""); setResult(null); setShowRaw(false);
    setAgentPhase({ news: "idle", rag: "idle", risk: "idle" });
    setAgentStatus({ news: "", rag: "", risk: "" });
    [120, 700, 1300].forEach((delay, i) =>
      setTimeout(() => setAgentPhase(p => ({ ...p, [AGENTS[i].id]: "running" })), delay));
    abort.current = new AbortController();
    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker: t }),
        signal: abort.current.signal,
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail ?? `HTTP ${res.status}`); }
      const data = await res.json();
      setAgentPhase({ news: "done", rag: "done", risk: "done" });
      setAgentStatus({ news: data.agent_status?.news ?? "complete", rag: data.agent_status?.rag ?? "complete", risk: data.agent_status?.risk ?? "complete" });
      setResult(data); setPhase("done");
    } catch (e) {
      if (e.name === "AbortError") return;
      setAgentPhase({ news: "error", rag: "error", risk: "error" });
      setError(e.message); setPhase("error");
    }
  };

  const sections = result ? parseBrief(result.brief) : [];
  const active = phase === "running" || phase === "done";

  return (
    <>
      <style>{css}</style>
      <div className="wrap">

        <header className="hdr">
          <div>
            <div className="brand">Fin<span>Scope</span></div>
            <div className="tagline">Multi-Agent Financial Intelligence System</div>
          </div>
          <div className="hdr-badge">v1.0 · LangGraph</div>
        </header>

        <div className="modules-label">Intelligence Pipeline</div>
        <div className="modules">
          {AGENTS.map(a => (
            <div key={a.id} className={`module ${agentPhase[a.id]}`}>
              <div className="module-top">
                <span className="module-tag">{a.tag}</span>
                <div className="module-icon" style={{ borderColor: a.color, color: a.color }}>
                  {a.id === "news" ? "N" : a.id === "rag" ? "R" : "K"}
                </div>
              </div>
              <div className="module-name" style={{ color: a.color }}>{a.label}</div>
              <div className="module-tech">{a.tech}</div>
              <div className="module-desc">{a.desc}</div>
              <div className="module-status" style={{ color: a.color }}>
                {agentPhase[a.id] === "running" && "● Processing..."}
                {agentPhase[a.id] === "done" && `✓ ${agentStatus[a.id] || "Complete"}`}
                {agentPhase[a.id] === "error" && "✗ Error"}
              </div>
              <div className="module-bar" style={{ background: a.color }} />
            </div>
          ))}
        </div>

        <div className="flow">
          {FLOW_NODES.map((n, i) => (
            <span key={n}>
              <span className={`flow-node ${active ? "active" : ""}`}>{n}</span>
              {i < FLOW_NODES.length - 1 && <span className="flow-arrow">──▶</span>}
            </span>
          ))}
        </div>

        <div className="input-section">
          <div className="input-box">
            <div className="input-row">
              <div className="ticker-wrap">
                <input className="ticker-in" placeholder="TICKER" value={ticker}
                  onChange={e => setTicker(e.target.value.toUpperCase())}
                  onKeyDown={e => e.key === "Enter" && run()}
                  disabled={phase === "running"} maxLength={10} spellCheck={false} autoComplete="off" />
              </div>
              <button className="run-btn" onClick={() => run()} disabled={phase === "running" || !ticker.trim()}>
                {phase === "running" ? "Running..." : "Run Analysis"}
              </button>
            </div>
          </div>
          <div className="quick-row">
            <span className="quick-lbl">Quick:</span>
            {QUICK.map(t => (
              <button key={t} className="chip" disabled={phase === "running"}
                onClick={() => { setTicker(t); run(t); }}>{t}</button>
            ))}
          </div>
        </div>

        {phase === "error" && <div className="err">⚠ {error}</div>}

        {phase === "done" && result && (
          <div className="results">
            <div className="results-hdr">
              <div className="results-ticker">{result.ticker}</div>
              <div className="results-meta">Analyst Brief · {result.elapsed_seconds}s · {new Date().toLocaleTimeString()}</div>
            </div>
            <div className="sections">
              {sections.length > 0
                ? sections.map((s, i) => <Section key={i} idx={i} title={s.title} body={s.body} />)
                : <Section idx={0} title="Analyst Brief" body={result.brief} />}
            </div>
            <div className="raw-row">
              <button className="raw-btn" onClick={() => setShowRaw(v => !v)}>
                {showRaw ? "Hide Raw" : "View Raw Brief"}
              </button>
            </div>
            {showRaw && <pre className="raw-pre">{result.brief}</pre>}
          </div>
        )}

        <footer className="footer">
          <div className="footer-brand">FinScope</div>
          <div className="stack-tags">{STACK.map(s => <span key={s} className="stack-tag">{s}</span>)}</div>
        </footer>

      </div>
    </>
  );
}
