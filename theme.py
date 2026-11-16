"""All the looks live here (CSS, animated hero, KPI cards, chart theme). app.py stays about data."""
import streamlit as st
import streamlit.components.v1 as components

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@500;600&display=swap');
.stApp h1,.stApp h2,.stApp h3,.stApp label,.stApp [data-testid="stMarkdownContainer"],button[data-baseweb="tab"]{font-family:'Space Grotesk',system-ui,sans-serif}
.stApp{background:radial-gradient(900px 500px at 85% -10%,rgba(167,139,250,.18),transparent 60%),radial-gradient(700px 400px at 0% 10%,rgba(34,211,238,.14),transparent 60%),#0b1020}
.stApp::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
 background-image:linear-gradient(rgba(34,211,238,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(34,211,238,.05) 1px,transparent 1px);
 background-size:48px 48px;animation:grid 24s linear infinite}
@keyframes grid{to{background-position:48px 48px}}
header[data-testid="stHeader"]{background:transparent}
.block-container{position:relative;z-index:1;padding-top:1.5rem;max-width:1250px}
.stApp h2,.stApp h3{background:linear-gradient(90deg,#22d3ee,#a78bfa);-webkit-background-clip:text;background-clip:text;color:transparent;width:fit-content}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0e1530,#0b1020);border-right:1px solid rgba(34,211,238,.15)}
.brand{display:flex;align-items:center;gap:10px;padding:6px 0 14px;border-bottom:1px solid rgba(148,163,184,.15);margin-bottom:10px}
.brand .logo{font-size:26px;animation:pulse 2.4s ease-in-out infinite}
.brand b{font-size:18px;display:block;line-height:1.1}.brand span{font-size:11px;color:#94a3b8;letter-spacing:.1em;text-transform:uppercase}
@keyframes pulse{50%{transform:scale(1.15);filter:drop-shadow(0 0 8px #22d3ee)}}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:6px 0 20px}
.kpi{position:relative;overflow:hidden;padding:16px 18px;border-radius:16px;background:linear-gradient(160deg,rgba(255,255,255,.07),rgba(255,255,255,.02));
 border:1px solid rgba(148,163,184,.18);backdrop-filter:blur(8px);animation:rise .6s both;transition:transform .25s,border-color .25s,box-shadow .25s}
.kpi:hover{transform:translateY(-4px);border-color:rgba(34,211,238,.6);box-shadow:0 10px 30px rgba(34,211,238,.15)}
.kpi::after{content:"";position:absolute;top:0;left:-60%;width:40%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);transform:skewX(-20deg);animation:sheen 6s infinite}
.kpi .ico{position:absolute;right:14px;top:12px;font-size:22px;animation:float 3s ease-in-out infinite}
.kpi .lab{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#94a3b8}
.kpi .val{font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:600;margin:4px 0 8px;color:#f1f5f9}
.chip{display:inline-block;font-size:12px;padding:2px 9px;border-radius:999px}
.chip.up{background:rgba(52,211,153,.15);color:#34d399}.chip.dn{background:rgba(248,113,113,.15);color:#f87171}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes sheen{0%,60%{left:-60%}100%{left:140%}}
@keyframes float{50%{transform:translateY(-4px)}}
[data-baseweb="tab-list"]{gap:8px;background:rgba(255,255,255,.03);padding:6px;border-radius:14px;border:1px solid rgba(148,163,184,.15)}
button[data-baseweb="tab"]{border-radius:10px;padding:8px 16px;background:transparent;transition:background .2s}
button[data-baseweb="tab"]:hover{background:rgba(34,211,238,.1)}
button[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(90deg,rgba(34,211,238,.25),rgba(167,139,250,.25))}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none}
[data-baseweb="tab-panel"]{animation:rise .45s both;padding-top:14px}
.stButton>button{background:linear-gradient(90deg,#06b6d4,#8b5cf6);color:#fff;border:0;border-radius:12px;padding:.55rem 1.2rem;font-weight:600;transition:transform .2s,box-shadow .2s}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(139,92,246,.4);color:#fff}
[data-testid="stMetric"]{background:rgba(255,255,255,.04);border:1px solid rgba(148,163,184,.18);border-radius:14px;padding:12px 16px}
[data-testid="stExpander"]{border:1px solid rgba(148,163,184,.18);border-radius:12px;background:rgba(255,255,255,.03)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

HERO = """
<style>
body{margin:0;background:transparent;font-family:'Space Grotesk',system-ui,sans-serif;color:#e6edf7}
.hero{position:relative;height:190px;border-radius:18px;overflow:hidden;border:1px solid rgba(34,211,238,.28);
 background:linear-gradient(135deg,#0f1b3d,#1a1040 60%,#0b1020);box-shadow:0 0 40px rgba(34,211,238,.12) inset}
canvas{position:absolute;inset:0;width:100%;height:100%}
.txt{position:relative;z-index:1;padding:26px 32px}
.live{display:inline-flex;align-items:center;gap:8px;font:600 11px 'JetBrains Mono',monospace;letter-spacing:.14em;color:#34d399}
.live i{width:8px;height:8px;border-radius:50%;background:#34d399;box-shadow:0 0 0 0 rgba(52,211,153,.7);animation:ping 1.8s infinite}
@keyframes ping{70%{box-shadow:0 0 0 10px rgba(52,211,153,0)}100%{box-shadow:0 0 0 0 rgba(52,211,153,0)}}
h1{margin:8px 0 6px;font-size:clamp(20px,3vw,34px);line-height:1.15;background:linear-gradient(90deg,#22d3ee,#a78bfa,#f472b6,#22d3ee);background-size:250% 100%;
 -webkit-background-clip:text;background-clip:text;color:transparent;animation:shine 6s linear infinite}
@keyframes shine{to{background-position:250% 0}}
.chips span{display:inline-block;margin:4px 6px 0 0;padding:3px 11px;font-size:12px;border-radius:999px;border:1px solid rgba(148,163,184,.3);background:rgba(255,255,255,.05);color:#cbd5e1}
.ring{position:absolute;right:34px;top:26px;width:120px;height:120px;z-index:1;opacity:.85}
.ring .a{transform-origin:60px 60px;animation:spin 14s linear infinite}.ring .b{transform-origin:60px 60px;animation:spin 9s linear infinite reverse}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:700px){.ring{display:none}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
<div class="hero">
<canvas id="c"></canvas>
<svg class="ring" viewBox="0 0 120 120" fill="none">
<circle class="a" cx="60" cy="60" r="54" stroke="#22d3ee" stroke-width="1.5" stroke-dasharray="6 8"/>
<circle class="b" cx="60" cy="60" r="40" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="2 6"/>
<polyline points="28,78 46,58 60,68 78,42 94,50" stroke="#f472b6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="78" cy="42" r="4" fill="#22d3ee"/></svg>
<div class="txt">
<div class="live"><i></i>LIVE ANALYSIS</div>
<h1>AI Business Strategy &amp; Executive Decision Intelligence</h1>
<div class="chips"><span>📊 KPIs</span><span>🔍 Anomalies</span><span>💬 Feedback</span><span>🎛️ Scenarios</span><span>🤖 GenAI</span></div>
</div></div>
<script>
const c=document.getElementById('c'),x=c.getContext('2d'),dpr=window.devicePixelRatio||1;
const W=()=>c.offsetWidth,H=()=>c.offsetHeight;
function size(){c.width=W()*dpr;c.height=H()*dpr;x.setTransform(dpr,0,0,dpr,0,0)}
size();addEventListener('resize',size);
const G=["{ }","01","</>","∑","AI","%","↗","Δ","#"];
const P=Array.from({length:50},()=>({x:Math.random()*W(),y:Math.random()*H(),vx:(Math.random()-.5)*.45,vy:(Math.random()-.5)*.45,g:Math.random()<.22?G[Math.floor(Math.random()*G.length)]:null}));
function frame(){x.clearRect(0,0,W(),H());
 for(const p of P){p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W())p.vx*=-1;if(p.y<0||p.y>H())p.vy*=-1;
  if(p.g){x.fillStyle='rgba(167,139,250,.6)';x.font='14px monospace';x.fillText(p.g,p.x,p.y)}
  else{x.fillStyle='rgba(34,211,238,.85)';x.beginPath();x.arc(p.x,p.y,1.8,0,6.283);x.fill()}}
 for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const d=Math.hypot(P[i].x-P[j].x,P[i].y-P[j].y);
  if(d<110){x.strokeStyle='rgba(34,211,238,'+(.2*(1-d/110))+')';x.beginPath();x.moveTo(P[i].x,P[i].y);x.lineTo(P[j].x,P[j].y);x.stroke()}}
 if(!matchMedia('(prefers-reduced-motion: reduce)').matches)requestAnimationFrame(frame)}
frame();
</script>
"""


def inject():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def hero():
    if hasattr(st, "iframe"):  # newer Streamlit
        st.iframe(HERO, height=205)
    else:  # older Streamlit
        components.html(HERO, height=205)


def brand():
    st.sidebar.markdown('<div class="brand"><div class="logo">⚡</div><div><b>Dino-Doc</b><span>executive intelligence</span></div></div>',
                        unsafe_allow_html=True)


def kpi_cards(items):
    """items: (icon, label, value, delta_text, is_good)"""
    cards = ""
    for i, (icon, label, value, delta, good) in enumerate(items):
        cls, arrow = ("up", "▲") if good else ("dn", "▼")
        cards += (f'<div class="kpi" style="animation-delay:{i * 0.08}s"><div class="ico">{icon}</div>'
                  f'<div class="lab">{label}</div><div class="val">{value}</div>'
                  f'<span class="chip {cls}">{arrow} {delta}</span></div>')
    st.markdown(f'<div class="kpis">{cards}</div>', unsafe_allow_html=True)


def style(fig):
    """Make Plotly charts match the dark theme."""
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      colorway=["#22d3ee", "#a78bfa", "#f472b6", "#34d399", "#fbbf24"],
                      margin=dict(l=10, r=10, t=50, b=10), font=dict(color="#cbd5e1"))
    fig.update_xaxes(gridcolor="rgba(148,163,184,.12)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)")
    return fig
