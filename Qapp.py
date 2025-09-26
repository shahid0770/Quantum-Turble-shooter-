"""
Quantum AI Assistant – Enhanced All-in-One Solution
With advanced features, improved UI, and expanded capabilities
"""

# ===== Imports =====
import streamlit as st
import random, json, time, logging, asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import qrcode
from io import BytesIO
import base64

# ===== Config =====
CONFIG = {
    "APP_TITLE": "Quantum AI Assistant Pro",
    "APP_ICON": "⚛️",
    "CHAT_HEIGHT": 500,
    "MAX_SOLUTIONS": 8,
    "SIMULATION_DELAY": 0.4,
    "PROGRESS_STEPS": 100,
    "KB_FILE": "knowledge_base.json",
    "HISTORY_FILE": "chat_history.json",
    "QUANTUM_RANDOMNESS_FACTOR": 0.15,
    "MIN_SIMILARITY_THRESHOLD": 0.1,
    "THEMES": ["Light", "Dark", "Quantum Blue", "Cyberpunk"],
    "LANGUAGES": ["English", "Spanish", "French", "German", "Japanese"],
}
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("QAI Pro")

# ===== Custom CSS =====
def inject_custom_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #6366f1;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #4f46e5;
        border-bottom: 2px solid #6366f1;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    .chat-user {
        background-color: #e0e7ff;
        padding: 1rem;
        border-radius: 1rem 1rem 0 1rem;
        margin: 0.5rem 0;
        border: 1px solid #c7d2fe;
    }
    .chat-bot {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 1rem 1rem 1rem 0;
        margin: 0.5rem 0;
        border: 1px solid #bae6fd;
    }
    .stButton button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .problem-card {
        background-color: #f8fafc;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #6366f1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s;
    }
    .problem-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #f1f5f9;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ===== Enums & Data =====
class Nav(Enum):
    CHAT = "Chat"
    KNOWLEDGE = "Knowledge Base"
    QUANTUM = "Quantum Process"
    ANALYTICS = "Analytics"
    SETTINGS = "Settings"
    ABOUT = "About"

class Role(Enum):
    USER = "user"
    BOT = "assistant"

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

@dataclass
class Message:
    role: Role
    content: str
    timestamp: str
    priority: Optional[Priority] = None
    helpful: Optional[bool] = None

class ComingSoon(NotImplementedError):
    pass

# ===== Knowledge Base =====
def load_kb(file: str = CONFIG["KB_FILE"]) -> Dict[str, List[str]]:
    """
    Loads KB or returns default with expanded categories
    """
    default = {
        # --- Digital / IT ---
        "password reset": [
            "Click **Forgot Password** on the login page.",
            "If 2FA is enabled, approve the push request.",
            "Contact IT if reset email not received within 15 minutes.",
            "⚠️ Error: *Reset link expired* → Request again with fresh link",
            "Check spam/junk folder for reset emails"
        ],
        "slow computer": [
            "Restart & close heavy applications using Task Manager",
            "Run a malware scan with Windows Defender or third-party antivirus",
            "Check **Task Manager** for high CPU/memory processes",
            "Upgrade to SSD for significant speed improvement",
            "Clear temporary files with Disk Cleanup utility",
            "Disable unnecessary startup programs"
        ],
        "wifi not connecting": [
            "Toggle Airplane mode or reboot router and modem",
            "Forget network and reconnect with correct credentials",
            "Check if DHCP is enabled in network adapter settings",
            "Error: *IP address conflict* – renew IP via command prompt: ipconfig /release then ipconfig /renew",
            "Update network adapter drivers from manufacturer website",
            "Check router firmware updates"
        ],
        "bluetooth issue": [
            "Turn off/on Bluetooth from system tray or settings",
            "Remove & re-pair device in Bluetooth settings",
            "Update drivers from Device Manager (devmgmt.msc)",
            "Run Bluetooth troubleshooter in Windows Settings",
            "Check if device is in pairing mode and discoverable"
        ],
        "printer offline": [
            "Ensure printer & PC are on same network (check IP addresses)",
            "Restart Print Spooler service (services.msc → Spooler)",
            "Re-install latest drivers from manufacturer website",
            "Check printer status on physical display for errors",
            "Clear print queue and restart printing"
        ],
        "excel formula error": [
            "Check `=` sign at start of formula entry",
            "Use absolute refs `$A$1` if copying formula across cells",
            "Error: `#VALUE!` – check for wrong data types in referenced cells",
            "Error: `#REF!` – referenced cells may have been deleted",
            "Use Formula Auditing tools to trace precedents/dependents",
            "Wrap complex formulas with IFERROR for cleaner sheets"
        ],
        "zoom mic not working": [
            "Check mute button & OS mic permissions in Sound Settings",
            "Choose correct audio device in Zoom settings → Audio",
            "Restart audio service (services.msc → Windows Audio)",
            "Test microphone in Windows Sound Settings → Input",
            "Check if Zoom has audio permissions in browser/app settings"
        ],

        # --- Mobile / Day-to-day ---
        "phone overheating": [
            "Close unused apps running in background",
            "Remove case while charging to improve heat dissipation",
            "Avoid gaming or video streaming while charging",
            "Check for software updates that may address thermal management",
            "Reduce screen brightness and timeout settings"
        ],
        "camera blurry": [
            "Clean lens with microfiber cloth (no liquids directly on lens)",
            "Disable beauty filter or other enhancement features",
            "Reset camera settings to default and retest",
            "Check for protective film or case obstructing lens",
            "Test in different lighting conditions - low light often causes blur"
        ],
        "battery drains fast": [
            "Reduce screen brightness and enable adaptive brightness",
            "Disable GPS, Bluetooth, and WiFi when not in use",
            "Check battery health in settings (usually under Battery section)",
            "Identify battery-hungry apps in Battery Usage settings",
            "Enable battery saver mode during critical times",
            "Consider battery replacement if health is below 80%"
        ],

        # --- Work / Productivity ---
        "outlook not syncing": [
            "Restart Outlook in safe mode: outlook.exe /safe",
            "Clear cached credentials in Credential Manager",
            "Check server status at `status.office.com`",
            "Rebuild OST/PST files if corrupted (may require admin help)",
            "Check mailbox size limits and archive old items"
        ],
        "vpn not connecting": [
            "Verify login credentials and network connectivity",
            "Restart VPN client service or reinstall client software",
            "Error: `TLS handshake failed` – update VPN client to latest version",
            "Check firewall settings aren't blocking VPN connection",
            "Try different VPN protocols (e.g., switch from UDP to TCP)"
        ],
        "remote desktop lag": [
            "Lower display resolution and color depth in RDP settings",
            "Disable printer/clipboard sharing to reduce bandwidth",
            "Use wired network connection instead of WiFi",
            "Check resource usage on both local and remote machines",
            "Adjust experience settings to match connection speed"
        ],

        # --- Mid-advanced / Dev ---
        "python import error": [
            "Activate correct virtual environment for your project",
            "Check `PYTHONPATH` environment variable and package installation",
            "Error: `ModuleNotFoundError` → pip install the missing package",
            "Check for circular imports in your code structure",
            "Verify file __init__.py exists in package directories",
            "Consider using conda environments for complex scientific packages"
        ],
        "git merge conflict": [
            "Run `git status` to see conflicted files",
            "Edit each file to keep correct code segments (look for conflict markers)",
            "Stage resolved files with `git add <filename>`",
            "Commit resolved files with `git commit -m 'Merge conflict resolution'`",
            "Use visual tools like VS Code's merge conflict editor or git mergetool",
            "For complex conflicts, consider aborting merge and rebasing instead"
        ],
        "docker build failed": [
            "Check Dockerfile syntax and base image references",
            "Increase disk space with `docker system prune`",
            "Error: `no space left on device` → prune images, containers, and volumes",
            "Check build context doesn't include unnecessary large files",
            "Use multi-stage builds to reduce final image size",
            "Review layer caching to optimize build process"
        ],

        # --- OS / Files ---
        "disk space low": [
            "Empty recycle bin/trash and temporary files (%temp%)",
            "Uninstall unused applications via Settings → Apps",
            "Move large files to cloud storage or external drives",
            "Use Storage Sense in Windows to automatically free space",
            "Analyze disk usage with tools like WinDirStat or TreeSize",
            "Clear browser caches and downloaded files"
        ],
        "file permission denied": [
            "Run as Administrator (right-click → Run as Administrator)",
            "Change file ownership in Properties → Security → Advanced",
            "On Linux use `sudo chmod` or `sudo chown` commands",
            "Check if file is in use by another process or application",
            "Take ownership of files/folders with administrative privileges"
        ],
        
        # --- New Categories ---
        "email hacked": [
            "Immediately change password and enable 2-factor authentication",
            "Check recent activity for suspicious logins",
            "Revoke access to suspicious third-party apps",
            "Scan device for malware/keyloggers",
            "Notify contacts about potential compromise",
            "Set up account recovery options"
        ],
        "software crashing": [
            "Update to latest version of the software",
            "Check compatibility with your operating system version",
            "Reinstall the application to fix corrupted files",
            "Check event viewer for specific error codes",
            "Run in compatibility mode if recently upgraded OS"
        ],
        "no internet connection": [
            "Reboot modem and router (unplug for 30 seconds)",
            "Check physical connections and cables",
            "Test with multiple devices to isolate problem",
            "Contact ISP to check for outages in your area",
            "Reset network stack with command: netsh winsock reset"
        ]
    }

    try:
        if Path(file).exists():
            return json.load(open(file, "r", encoding="utf8"))
    except Exception as e:
        log.warning(f"KB load failed: {e}")
    return default

def save_kb(kb_data: Dict[str, List[str]], file: str = CONFIG["KB_FILE"]):
    """Save knowledge base to file"""
    try:
        with open(file, "w", encoding="utf8") as f:
            json.dump(kb_data, f, indent=2)
        return True
    except Exception as e:
        log.error(f"Failed to save KB: {e}")
        return False

# ===== Core Logic =====
class QuantumSearch:
    def __init__(self, kb: Dict[str, List[str]]):
        self.kb = kb
        self.problems = list(kb.keys())
        self.search_history = []

    def _similarity(self, q: str, p: str) -> float:
        try:
            q_w, p_w = set(q.lower().split()), set(p.lower().split())
            if not q_w or not p_w:
                return 0.0
            # Calculate Jaccard similarity with quantum randomness factor
            intersection = len(q_w & p_w)
            union = len(q_w | p_w)
            j = intersection / union if union > 0 else 0
            
            # Add quantum randomness factor for simulation
            quantum_factor = CONFIG["QUANTUM_RANDOMNESS_FACTOR"] * random.random()
            return min(1.0, j + quantum_factor)
        except Exception as e:
            log.error(e)
            return 0.0

    def search(self, query: str, n: int = 5) -> List[str]:
        if query.strip().lower() == "simulate error":
            raise RuntimeError("💥 Simulated quantum decoherence event")
            
        if query.strip().lower() == "quantum flux":
            raise RuntimeError("🪐 Quantum flux capacitor malfunction")
            
        # Record search for analytics
        self.search_history.append({
            "query": query, 
            "timestamp": datetime.now().isoformat()
        })
        
        scored = [(p, self._similarity(query, p)) for p in self.problems]
        scored = [x for x in scored if x[1] >= CONFIG["MIN_SIMILARITY_THRESHOLD"]]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        out = []
        for p, score in scored[:n]:
            if score > 0.5:  # High confidence matches
                out.extend(self.kb[p])
            elif score > 0.3:  # Medium confidence - add prefix
                out.extend([f"Possible match: {s}" for s in self.kb[p]])
            else:  # Low confidence
                out.extend([f"Related idea: {s}" for s in self.kb[p][:1]])
                
        return out[:CONFIG["MAX_SOLUTIONS"]]

    def get_search_stats(self):
        """Return search statistics for analytics"""
        if not self.search_history:
            return {"total": 0, "recent": 0, "trending": []}
        
        # Calculate basic stats
        total = len(self.search_history)
        recent = len([s for s in self.search_history 
                     if datetime.fromisoformat(s["timestamp"]) > datetime.now() - timedelta(hours=24)])
        
        # Find trending queries (simplified)
        queries = [s["query"] for s in self.search_history[-20:]]  # Last 20 queries
        trending = []
        if queries:
            from collections import Counter
            trending = Counter(queries).most_common(3)
            
        return {
            "total": total,
            "recent": recent,
            "trending": trending
        }

class LLM:
    def __init__(self):
        self.templates = [
            "🔍 Quantum analysis complete: {solution}",
            "💡 Quantum suggestion: {solution}",
            "🚀 Quantum solution: {solution}",
            "⚛️ Quantum algorithm suggests: {solution}",
            "🌌 Multiverse analysis indicates: {solution}"
        ]
        self.fallback_responses = [
            "I've consulted the quantum realm but didn't find a precise match. Could you provide more details?",
            "The quantum probabilities are uncertain on this topic. Try rephrasing your question.",
            "My quantum circuits are having interference with this query. Please try again with different words.",
            "The multiverse suggests several possibilities, but none stand out clearly. Could you elaborate?",
            "Quantum entanglement has confused my response. Please ask again with more context."
        ]

    def reply(self, sols: List[str]) -> str:
        if not sols:
            return random.choice(self.fallback_responses)
            
        base = random.choice(self.templates).format(solution=sols[0])
        if len(sols) > 1:
            base += "\n\n**Additional quantum insights:**\n" + "\n".join(f"• {s}" for s in sols[1:4])
        if len(sols) > 4:
            base += f"\n\n*And {len(sols)-4} more quantum possibilities...*"
            
        return base

class Chatbot:
    def __init__(self):
        self.kb = load_kb()
        self.searcher = QuantumSearch(self.kb)
        self.llm = LLM()
        self.session_start = datetime.now()
        self.session_queries = 0

    def process(self, q: str) -> str:
        self.session_queries += 1
        ql = q.strip().lower()
        
        # Special commands
        if ql == "voice support":
            raise ComingSoon("🎙️ Voice Support is coming in the next quantum update.")
        if ql == "dark mode":
            raise ComingSoon("🌙 Dark Mode is being tuned for optimal quantum viewing.")
        if ql == "quantum stats":
            return f"📊 Quantum Stats: {self.session_queries} queries this session, {len(self.searcher.search_history)} total searches."
        if ql == "help":
            return "**Quantum Assistant Help:**\n• Describe your technical issue\n• Use 'quantum stats' for analytics\n• Try 'simulate error' for testing\n• Use clear, specific questions for best results"
            
        # Process query
        sols = self.searcher.search(q)
        return self.llm.reply(sols)
    
    def get_session_stats(self):
        duration = datetime.now() - self.session_start
        return {
            "queries": self.session_queries,
            "duration": str(duration).split(".")[0],  # Remove microseconds
            "start_time": self.session_start.strftime("%H:%M:%S")
        }

# ===== UI Components =====
def create_problem_card(title, solutions, key):
    with st.expander(title, expanded=False):
        for i, solution in enumerate(solutions):
            st.markdown(f"{i+1}. {solution}")
        if st.button("Apply this solution", key=f"btn_{key}"):
            st.session_state.msgs.append(Message(
                Role.USER, f"Applied solution for {title}", datetime.now().strftime("%H:%M:%S")
            ))
            st.session_state.msgs.append(Message(
                Role.BOT, f"✅ Applied solution for {title}. Let me know if you need further assistance!", 
                datetime.now().strftime("%H:%M:%S")
            ))
            st.rerun()

def generate_qr_code(data: str) -> str:
    """Generate a QR code and return as data URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#6366f1", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def chart_quantum_process() -> go.Figure:
    # Create a visualization of quantum process
    steps = ['Init', 'Superposition', 'Entanglement', 'Measurement', 'Result']
    values = [0, 4, 7, 9, 10]
    
    fig = go.Figure(go.Scatter(
        x=steps, y=values,
        mode='lines+markers+text',
        line=dict(color='#6366f1', width=4),
        marker=dict(size=12, color=['#e5e7eb', '#c7d2fe', '#a5b4fc', '#818cf8', '#6366f1']),
        text=[f'Step {i+1}' for i in range(5)],
        textposition="top center"
    ))
    
    fig.update_layout(
        title="Quantum Solution Process",
        xaxis_title="Quantum Steps",
        yaxis_title="Certainty Level",
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def chart_usage_metrics(bot: Chatbot):
    # Create usage metrics
    stats = bot.searcher.get_search_stats()
    
    fig = go.Figure()
    
    # Add metrics as a bar chart
    fig.add_trace(go.Bar(
        x=['Total Searches', 'Last 24h'],
        y=[stats['total'], stats['recent']],
        marker_color=['#6366f1', '#8b5cf6']
    ))
    
    fig.update_layout(
        title="Search Metrics",
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

# ===== UI Sections =====
def ui_chat(bot: Chatbot):
    st.markdown('<div class="sub-header">💬 Quantum Chat Assistant</div>', unsafe_allow_html=True)
    
    # Chat container with custom styling
    chat_container = st.container(height=CONFIG["CHAT_HEIGHT"])
    with chat_container:
        for i, m in enumerate(st.session_state.msgs):
            if m.role == Role.USER:
                st.markdown(f"""
                <div class="chat-user">
                    <strong>You</strong> ({m.timestamp}):<br>
                    {m.content}
                </div>
                """, unsafe_allow_html=True)
            else:
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(f"""
                    <div class="chat-bot">
                        <strong>Quantum AI</strong> ({m.timestamp}):<br>
                        {m.content}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if m.helpful is None:
                        if st.button("✓", key=f"helpful_{i}"):
                            m.helpful = True
                            st.rerun()
                        if st.button("✗", key=f"unhelpful_{i}"):
                            m.helpful = False
                            st.rerun()
                    else:
                        st.markdown("✓" if m.helpful else "✗")
    
    # Chat input with options
    input_col, button_col = st.columns([0.8, 0.2])
    with input_col:
        txt = st.chat_input("Describe your quantum issue...")
    with button_col:
        if st.button("Clear Chat"):
            st.session_state.msgs = []
            st.rerun()
    
    if txt:
        st.session_state.msgs.append(Message(Role.USER, txt, datetime.now().strftime("%H:%M:%S")))
        
        # Show quantum processing animation
        with st.status("Quantum processing...", expanded=False) as status:
            st.write("Initializing qubits...")
            progress_bar = st.progress(0)
            
            for i in range(CONFIG["PROGRESS_STEPS"]):
                time.sleep(CONFIG["SIMULATION_DELAY"] / CONFIG["PROGRESS_STEPS"])
                progress_bar.progress(i + 1)
                
                if i == 20:
                    st.write("Creating superposition...")
                elif i == 40:
                    st.write("Entangling quantum states...")
                elif i == 60:
                    st.write("Collapsing wave function...")
                elif i == 80:
                    st.write("Interpreting results...")
            
            try:
                ans = bot.process(txt)
                status.update(label="Quantum analysis complete!", state="complete")
            except ComingSoon as e:
                ans = f"🚧 {e}"
                status.update(label="Feature coming soon!", state="complete")
            except Exception as e:
                ans = f"⚠️ Quantum instability: {e}"
                status.update(label="Quantum error detected!", state="error")
        
        st.session_state.msgs.append(Message(Role.BOT, ans, datetime.now().strftime("%H:%M:%S")))
        st.rerun()

def ui_kb(bot: Chatbot):
    st.markdown('<div class="sub-header">📚 Quantum Knowledge Base</div>', unsafe_allow_html=True)
    
    # Search and filter options
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        search_query = st.text_input("Search knowledge base...")
    with col2:
        category_filter = st.selectbox("Category", ["All"] + list(bot.kb.keys()))
    
    # Display knowledge base
    for topic, sols in bot.kb.items():
        if search_query and search_query.lower() not in topic.lower():
            continue
        if category_filter != "All" and topic != category_filter:
            continue
            
        create_problem_card(topic.title(), sols, topic)

def ui_quantum():
    st.markdown('<div class="sub-header">⚛️ Quantum Process Simulator</div>', unsafe_allow_html=True)
    
    st.plotly_chart(chart_quantum_process(), use_container_width=True)
    
    # Quantum process explanation
    with st.expander("How Quantum Computing Solves Problems", expanded=True):
        st.markdown("""
        Our quantum assistant uses simulated quantum algorithms to find solutions:
        
        1. **Qubit Initialization** - Your problem is encoded into quantum bits (qubits)
        2. **Superposition** - Qubits explore multiple solution paths simultaneously
        3. **Entanglement** - Quantum correlation between different solution possibilities
        4. **Measurement** - The most probable solution collapses from quantum state
        5. **Result** - Classical solution is extracted and presented
        
        *Note: This is a simulation of quantum processes on classical hardware.*
        """)
    
    # Interactive quantum circuit
    st.subheader("Interactive Quantum Circuit")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Apply Hadamard Gate", help="Creates superposition"):
            st.session_state.quantum_step = "superposition"
            st.rerun()
    
    with col2:
        if st.button("Apply CNOT Gate", help="Creates entanglement"):
            st.session_state.quantum_step = "entanglement"
            st.rerun()
    
    with col3:
        if st.button("Measure Qubits", help="Collapses to classical state"):
            st.session_state.quantum_step = "measurement"
            st.rerun()
    
    if "quantum_step" in st.session_state:
        if st.session_state.quantum_step == "superposition":
            st.info("🌀 Qubits now in superposition - exploring multiple states simultaneously")
        elif st.session_state.quantum_step == "entanglement":
            st.info("🔗 Qubits now entangled - quantum correlation established")
        elif st.session_state.quantum_step == "measurement":
            st.success("📊 Measurement complete - quantum state collapsed to solution")

def ui_analytics(bot: Chatbot):
    st.markdown('<div class="sub-header">📊 Quantum Analytics</div>', unsafe_allow_html=True)
    
    # Session stats
    session_stats = bot.get_session_stats()
    search_stats = bot.searcher.get_search_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Session Queries", session_stats["queries"])
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Searches", search_stats["total"])
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Recent Searches", search_stats["recent"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts
    st.plotly_chart(chart_usage_metrics(bot), use_container_width=True)
    
    # Trending queries
    st.subheader("Trending Queries")
    search_stats = bot.searcher.get_search_stats()
    if search_stats["trending"]:
        for query, count in search_stats["trending"]:
            st.markdown(f"- **{query}** ({count} searches)")
    else:
        st.info("No trending queries yet. Start chatting to generate analytics!")
    
    # Feedback analysis
    helpful_count = sum(1 for m in st.session_state.msgs if m.role == Role.BOT and m.helpful is True)
    unhelpful_count = sum(1 for m in st.session_state.msgs if m.role == Role.BOT and m.helpful is False)
    total_feedback = helpful_count + unhelpful_count
    
    if total_feedback > 0:
        st.subheader("Solution Feedback")
        feedback_data = pd.DataFrame({
            "Type": ["Helpful", "Unhelpful"],
            "Count": [helpful_count, unhelpful_count]
        })
        
        fig = px.pie(feedback_data, values="Count", names="Type", 
                    color_discrete_sequence=["#6366f1", "#ef4444"])
        st.plotly_chart(fig, use_container_width=True)

def ui_settings():
    st.markdown('<div class="sub-header">⚙️ Quantum Settings</div>', unsafe_allow_html=True)
    
    # Appearance settings
    st.subheader("Appearance")
    theme = st.selectbox("Theme", CONFIG["THEMES"], index=0)
    language = st.selectbox("Language", CONFIG["LANGUAGES"], index=0)
    
    # Chat settings
    st.subheader("Chat Preferences")
    st.slider("Chat History Length", 10, 100, 50, key="chat_history_length")
    st.checkbox("Show Quantum Animations", value=True, key="show_animations")
    st.checkbox("Voice Responses (when available)", value=False, key="voice_responses")
    
    # Notification settings
    st.subheader("Notifications")
    st.checkbox("Enable Notification Sounds", value=True, key="notification_sounds")
    st.checkbox("Desktop Alerts", value=False, key="desktop_alerts")
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
        
    # QR code for mobile access
    st.subheader("Mobile Access")
    st.markdown("Scan this QR code to access Quantum AI Assistant on your mobile device")
    qr_img = generate_qr_code("https://quantum-ai-assistant.streamlit.app")
    st.image(qr_img, caption="Quantum AI Assistant Mobile QR Code", width=200)

def ui_about():
    st.markdown('<div class="sub-header">🌌 About Quantum AI Assistant</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Quantum AI Assistant Pro** is an advanced troubleshooting system that uses quantum-inspired 
    algorithms to solve technical problems across multiple domains.
    
    ### Features
    - 🔍 **Quantum-Powered Search**: Finds solutions using quantum simulation algorithms
    - 📚 **Expanded Knowledge Base**: Hundreds of solutions for common technical issues
    - 📊 **Analytics Dashboard**: Track your search history and solution effectiveness
    - ⚛️ **Quantum Process Simulator**: Visualize how quantum computing solves problems
    - 🎨 **Beautiful Interface**: Modern, responsive design with custom themes
    
    ### Technology
    Built with:
    - Python & Streamlit for the frontend
    - Quantum-inspired search algorithms
    - Plotly for advanced visualizations
    - Custom CSS styling for enhanced UI/UX
    
    ### Version
    Quantum AI Assistant Pro v2.0
    """)
    
    # Team information
    with st.expander("Development Team"):
        st.markdown("""
        - **Lead Developer**: Dr. Quantum Smith
        - **UI/UX Designer**: Alice Designberg
        - **Knowledge Engineer**: Professor Data Wright
        - **Quantum Consultant**: Dr. Qubit Johnson
        """)
    
    # Social links
    st.subheader("Connect With Us")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("🌐 Website")
    with col2:
        st.button("📘 GitHub")
    with col3:
        st.button("🐦 Twitter")

# ===== Main =====
def main():
    # Initialize session state
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    if "theme" not in st.session_state:
        st.session_state.theme = CONFIG["THEMES"][0]
    
    # Setup page
    st.set_page_config(
        page_title=CONFIG["APP_TITLE"], 
        page_icon=CONFIG["APP_ICON"], 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize chatbot
    bot = Chatbot()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f'<div class="main-header">{CONFIG["APP_TITLE"]}</div>', unsafe_allow_html=True)
        
        # Navigation
        nav = option_menu(
            None, 
            [n.value for n in Nav], 
            icons=["chat", "database", "cpu", "bar-chart", "gear", "info-circle"],
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "#6366f1", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eef2ff"},
                "nav-link-selected": {"background-color": "#6366f1", "font-weight": "normal"},
            }
        )
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("**⚡ Quick Actions**")
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.msgs = []
            st.rerun()
            
        if st.button("Quantum Diagnostics", use_container_width=True):
            st.session_state.msgs.append(Message(
                Role.USER, "Run diagnostics", datetime.now().strftime("%H:%M:%S")
            ))
            st.session_state.msgs.append(Message(
                Role.BOT, "✅ Quantum systems nominal. All circuits functioning within parameters.", 
                datetime.now().strftime("%H:%M:%S")
            ))
            st.rerun()
            
        st.markdown("---")
        
        # Problem shortcuts
        st.markdown("**🔍 Common Problems**")
        problem_col1, problem_col2 = st.columns(2)
        
        common_problems = list(bot.kb.keys())[:6]  # First 6 problems
        for i, problem in enumerate(common_problems):
            col = problem_col1 if i % 2 == 0 else problem_col2
            with col:
                if st.button(problem.title(), key=f"shortcut_{problem}"):
                    st.session_state.msgs.append(Message(
                        Role.USER, problem, datetime.now().strftime("%H:%M:%S")
                    ))
                    ans = bot.process(problem)
                    st.session_state.msgs.append(Message(
                        Role.BOT, ans, datetime.now().strftime("%H:%M:%S")
                    ))
                    st.rerun()
        
        st.markdown("---")
        
        # Session info
        st.markdown("**📊 Current Session**")
        session_stats = bot.get_session_stats()
        st.markdown(f"Started: {session_stats['start_time']}")
        st.markdown(f"Queries: {session_stats['queries']}")
        st.markdown(f"Duration: {session_stats['duration']}")
        
        st.markdown("---")
        
        # QR code for mobile
        st.markdown("**📱 Mobile Access**")
        qr_img = generate_qr_code("https://quantum-ai-assistant.streamlit.app")
        st.image(qr_img, caption="Scan for mobile access", use_column_width=True)
    
    # Main content area
    if nav == Nav.CHAT.value:
        ui_chat(bot)
    elif nav == Nav.KNOWLEDGE.value:
        ui_kb(bot)
    elif nav == Nav.QUANTUM.value:
        ui_quantum()
    elif nav == Nav.ANALYTICS.value:
        ui_analytics(bot)
    elif nav == Nav.SETTINGS.value:
        ui_settings()
    elif nav == Nav.ABOUT.value:
        ui_about()

if __name__ == "__main__":
    main()