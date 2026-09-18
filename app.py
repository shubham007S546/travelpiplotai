"""TravelPilot AI — Modern Website-Grade Multi-Agent Travel Planning Application."""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Synchronize Streamlit Cloud secrets into os.environ
try:
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, (str, int, float, bool)):
                os.environ[str(k)] = str(v)
except Exception:
    pass

from orchestration.graph import travel_pipeline
from orchestration.state import create_initial_state
from models.travel_state import TravelState
from utils.api_audit import get_global_audit_log, clear_global_audit_log

# Import modular UI views
from ui.dashboard import render_dashboard
from ui.transport_view import render_transport_view
from ui.hotel_view import render_hotel_view
from ui.itinerary_view import render_itinerary_view
from ui.explore_places_view import render_explore_places_view
from ui.budget_view import render_budget_view
from ui.local_services_view import render_local_services_view
from ui.agent_trace_view import render_agent_trace_view
from ui.live_audit_view import render_live_audit_view
from services.rag_service import TravelRAGService
from services.pdf_service import generate_travel_pass_pdf


def get_live_api_catalog():
    """Returns comprehensive metadata for all live APIs utilized across the system."""
    return [
        {
            "name": "AviationStack Flight Telemetry",
            "active": bool(os.getenv("AVIATIONSTACK_API_KEY")),
            "capability": "Live Scheduled Commercial Flights, Airlines, Status & Air Route Tariffs",
            "engine": "api.aviationstack.com/v1/flights"
        },
        {
            "name": "SerpApi Google Maps & Hotels",
            "active": bool(os.getenv("SERPAPI_API_KEY")),
            "capability": "Live Google Maps Sights, Local Food/Dhabas & Budget Homestays/PGs",
            "engine": "google_maps, google_hotels"
        },
        {
            "name": "YouTube Data API v3",
            "active": bool(os.getenv("YOUTUBE_API_KEY")),
            "capability": "Live Travel Vlog Guides, Upload Year Verification & Tariff Audit",
            "engine": "googleapis.com/youtube/v3/search"
        },
        {
            "name": "Tavily Search Engine",
            "active": bool(os.getenv("TAVILY_API_KEY")),
            "capability": "Dynamic India Transit Grounding, Road-Heads & Camping Tent Rentals",
            "engine": "tavily.com/search"
        },
        {
            "name": "OpenWeatherMap Live API",
            "active": bool(os.getenv("OPENWEATHER_API_KEY")),
            "capability": "Real-Time Temperature, Rain Probability & Packing Advisories",
            "engine": "api.openweathermap.org/data/2.5/weather"
        },
        {
            "name": "OpenRouteService / OSRM",
            "active": bool(os.getenv("OPENROUTESERVICE_API_KEY")),
            "capability": "Verified Road Driving Distances, Durations & Cross-Routing Audit",
            "engine": "api.openrouteservice.org / project-osrm.org"
        },
        {
            "name": "OpenTripMap Global Registry",
            "active": bool(os.getenv("OPENTRIPMAP_API_KEY")),
            "capability": "Cultural, Heritage, Religious & Architectural Attractions Discovery",
            "engine": "api.opentripmap.com/0.1/en/places"
        },
        {
            "name": "Groq Cloud LLM",
            "active": bool(os.getenv("GROQ_API_KEY")),
            "capability": "High-Speed Agentic Reasoning & Contextual Synthesis (Llama-3)",
            "engine": "api.groq.com/openai/v1"
        },
        {
            "name": "ReportLab PDF Engine",
            "active": True,
            "capability": "High-Fidelity Printable PDF Travel Pass & Multi-Leg Schedule Export",
            "engine": "reportlab.platypus"
        }
    ]


def inject_global_website_styles():
    """Injects high-end web app CSS: custom fonts, glassmorphism, glowing badges, clean tabs, and complete sidebar removal."""
    st.markdown("""
    <style>
        /* Modern Font & Typography */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [class*="css"], .stMarkdown, .stText, div, p, span {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }

        /* HIDE STREAMLIT SIDEBAR COMPLETELY */
        [data-testid="stSidebar"], 
        [data-testid="stSidebarCollapsedControl"], 
        section[data-testid="stSidebar"],
        button[data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        /* HIDE STREAMLIT CHROME & WATERMARK */
        #MainMenu { visibility: hidden !important; }
        header[data-testid="stHeader"] { display: none !important; }
        footer { visibility: hidden !important; }
        
        /* FULL-WIDTH LUXURY CONTAINER */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1380px !important;
            margin: 0 auto !important;
        }

        /* TOP NAVIGATION NAVBAR */
        .tp-navbar {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 14px 24px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }
        .tp-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
        }
        .tp-brand-icon {
            font-size: 1.9rem;
            filter: drop-shadow(0 2px 8px rgba(56, 189, 248, 0.4));
        }
        .tp-brand-name {
            font-size: 1.45rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #FFFFFF 20%, #38BDF8 70%, #818CF8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            line-height: 1.1;
        }
        .tp-brand-badge {
            display: inline-block;
            background: rgba(56, 189, 248, 0.12);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 9999px;
            padding: 2px 10px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        /* MODERN HERO CONTAINER */
        .tp-hero-section {
            background: radial-gradient(circle at 50% -20%, rgba(14, 165, 233, 0.18) 0%, rgba(15, 23, 42, 0) 60%),
                        linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.85) 100%);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 24px;
            padding: 44px 36px 36px 36px;
            margin-bottom: 28px;
            text-align: center;
            position: relative;
            box-shadow: 0 20px 50px -15px rgba(0, 0, 0, 0.6);
        }
        .tp-hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(2, 132, 199, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #7DD3FC;
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 0.84rem;
            font-weight: 700;
            margin-bottom: 16px;
            letter-spacing: 0.03em;
        }
        .tp-hero-headline {
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.15;
            background: linear-gradient(135deg, #FFFFFF 30%, #E2E8F0 60%, #94A3B8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 auto 12px auto;
            max-width: 860px;
        }
        .tp-hero-subheadline {
            font-size: 1.05rem;
            color: #94A3B8;
            max-width: 720px;
            margin: 0 auto 24px auto;
            line-height: 1.6;
        }

        /* FEATURE HIGHLIGHT STRIP */
        .tp-feature-strip {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-bottom: 28px;
        }
        .tp-feature-item {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.2s ease;
        }
        .tp-feature-item:hover {
            background: rgba(30, 41, 59, 0.7);
            border-color: rgba(56, 189, 248, 0.3);
            transform: translateY(-2px);
        }
        .tp-feature-icon {
            font-size: 1.6rem;
            background: rgba(15, 23, 42, 0.6);
            width: 42px;
            height: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .tp-feature-text-title {
            font-size: 0.88rem;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 2px;
        }
        .tp-feature-text-sub {
            font-size: 0.76rem;
            color: #94A3B8;
        }

        /* CLEAN SEARCH CARD */
        .tp-search-card {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 24px;
            padding: 32px 36px 28px;
            box-shadow: 0 24px 60px -16px rgba(0,0,0,0.6);
            margin-bottom: 8px;
        }

        /* EXAMPLE CHIPS */
        .tp-chip-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 16px 0 24px;
        }

        /* FEATURE PILLS ROW */
        .tp-pill-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
            margin: 18px 0 32px;
        }
        .tp-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(30,41,59,0.6);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 9999px;
            padding: 6px 14px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #CBD5E1;
        }

        /* SLIM HERO */
        .tp-hero-slim {
            text-align: center;
            padding: 40px 20px 8px;
        }
        .tp-hero-slim h1 {
            font-size: 2.6rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.15;
            background: linear-gradient(135deg, #FFFFFF 30%, #7DD3FC 80%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 auto 10px;
        }
        .tp-hero-slim p {
            font-size: 1rem;
            color: #94A3B8;
            max-width: 560px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* TEXTAREA GLOW */
        .stTextArea textarea:focus {
            border-color: rgba(56,189,248,0.5) !important;
            box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
        }
        .stTextArea textarea {
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            background: rgba(15,23,42,0.7) !important;
            color: #F1F5F9 !important;
            font-size: 0.97rem !important;
            transition: border-color 0.2s, box-shadow 0.2s !important;
        }

        /* APP TOP TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background: rgba(15, 23, 42, 0.75);
            padding: 8px 12px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 24px;
            box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4);
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 12px;
            color: #94A3B8;
            font-size: 0.95rem;
            font-weight: 600;
            padding: 0 20px;
            transition: all 0.2s ease-in-out;
            border: 1px solid transparent;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #F8FAFC;
            background: rgba(255, 255, 255, 0.04);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 16px rgba(2, 132, 199, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }

        /* METRIC CARDS & INPUTS */
        .stMetric {
            background: rgba(30, 41, 59, 0.5) !important;
            padding: 14px 18px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
        }
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 12px 24px !important;
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.35) !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 24px rgba(2, 132, 199, 0.5) !important;
        }
        /* PRESET TAG */
        .tp-preset-tag {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            background: rgba(56, 189, 248, 0.15);
            color: #38BDF8;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)


def render_top_navbar(state: TravelState):
    """Renders the website top navbar with brand, API status popover, live telemetry, and reset actions."""
    nav_c1, nav_c2, nav_c3 = st.columns([4, 3, 2])
    
    with nav_c1:
        st.markdown("""
        <div class="tp-brand">
            <span class="tp-brand-icon">🧭</span>
            <div>
                <div class="tp-brand-name">TravelPilot AI</div>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 2px;">
                    <span class="tp-brand-badge">Multi-Agent Engine</span>
                    <span style="font-size: 0.78rem; color: #94A3B8;">Zero-Hallucination Travel System</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with nav_c2:
        total_calls = len(get_global_audit_log())
        with st.popover(f"🟢 8 Live API Engines Connected ({total_calls} Calls)", use_container_width=True):
            st.markdown("### ⚡ Connected Live API Catalog & Status")
            st.caption("Live external APIs queried during agent execution to enforce ground truth.")
            api_catalog = get_live_api_catalog()
            for api in api_catalog:
                badge = "🟢 Live" if api["active"] else "🟡 Standby"
                with st.container(border=True):
                    st.markdown(f"**{api['name']}** &nbsp; `{badge}`")
                    st.caption(f"**Capability:** {api['capability']}")
                    st.caption(f"**Endpoint:** `{api['engine']}`")

    with nav_c3:
        if st.button("🔄 Plan New Trip", use_container_width=True):
            st.session_state.pop("travel_state", None)
            st.session_state.pop("replan_banner", None)
            clear_global_audit_log()
            st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 8px 0 20px 0;'>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="TravelPilot AI - Grounded Multi-Agent Travel Planner",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Global Website Styles
    inject_global_website_styles()

    # State & Services
    state: TravelState = st.session_state.get("travel_state")
    rag_service = TravelRAGService()

    # Invisible top anchor
    st.markdown('<div id="plan-top"></div>', unsafe_allow_html=True)

    # Top Website Navigation Bar
    render_top_navbar(state)

    # If no trip plan exists, render the website landing hero + search console
    if state is None:
        st.session_state.pop("scroll_to_top", None)
        render_website_landing()
        return

    # Auto-scroll to top whenever the plan view is rendered
    st.markdown("""
    <script>
        (function() {
            var main = window.parent.document.querySelector('section.main');
            if (main) main.scrollTo({top: 0, behavior: 'smooth'});
            window.scrollTo({top: 0, behavior: 'smooth'});
        })();
    </script>
    """, unsafe_allow_html=True)

    # If a trip plan exists, render the modern dossier view with tabs
    render_active_trip_dossier(state, rag_service)


def render_website_landing():
    """Renders a clean, minimal landing page: slim hero → feature pills → search card → 2 example chips."""

    # ── 1. Slim Hero ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="tp-hero-slim">
        <div class="tp-hero-pill">✨ Verified Ground Truth &nbsp;·&nbsp; Zero Hallucination</div>
        <h1>Plan Your Trip, Powered by Real Data</h1>
        <p>Describe where you want to go and your budget — our AI verifies every bus fare,<br>
        hotel rate, and trail in real-time across 8 live APIs.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. Feature pills (single row) ────────────────────────────────────────
    st.markdown("""
    <div class="tp-pill-row">
        <span class="tp-pill">🛡️ Verified HRTC/IRCTC Fares</span>
        <span class="tp-pill">⛅ Live Weather</span>
        <span class="tp-pill">🎥 YouTube Vlog Grounding</span>
        <span class="tp-pill">⚡ Auto Budget Repair</span>
        <span class="tp-pill">🗺️ Real Road Distances</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 3. Search card (main input) ───────────────────────────────────────────
    render_input_form()

    # ── 4. Two compact example chips below the card ───────────────────────────
    st.caption("💡 Try an example:")
    chip_col1, chip_col2, chip_col3 = st.columns([3, 3, 4])
    with chip_col1:
        if st.button("🏔️ Sundernagar → Manali (₹3,000 · 3 days)", key="btn_sund_manali", use_container_width=True):
            st.session_state["query_input"] = (
                "I have ₹3,000. Plan a 3-day budget trip from Sundernagar to Manali. "
                "Use HRTC ordinary bus (change at Mandi ISBT), budget guesthouse in Old Manali, "
                "visit Hadimba Temple and Solang Valley."
            )
            st.rerun()
    with chip_col2:
        if st.button("🛕 Bhuntar → Bijli Mahadev (₹3,000 · 2 days)", key="btn_bhuntar_bijli", use_container_width=True):
            st.session_state["query_input"] = (
                "I have ₹3,000. I want to travel from Bhuntar to Bijli Mahadev Temple for 2 days. "
                "I want to camp and rent a tent. Use local HRTC bus and trek."
            )
            st.rerun()



def render_input_form(is_compact: bool = False):
    """Renders a clean, minimal search card with text area + submit + optional advanced params."""
    with st.container(border=True):
        st.markdown(
            "<div style='font-size:1.05rem; font-weight:700; color:#F1F5F9; margin-bottom:6px;'>"
            "🗺️ Where do you want to go?"
            "</div>",
            unsafe_allow_html=True
        )

        default_prompt = (
            "I have ₹3,000. I want to travel from Bhuntar to Bijli Mahadev Temple for 2 days. "
            "We want to camp and rent a tent over there. We want local bus transit and trek."
        )

        query_text = st.text_area(
            label="Travel request",
            label_visibility="collapsed",
            value=st.session_state.get("query_input", default_prompt),
            height=100,
            placeholder="e.g. ₹4,000 · 2 days · Delhi to Jaipur · budget homestay & local food",
            key="main_query_text"
        )

        with st.expander("⚙️ Advanced Parameters Override (Optional)", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                override_src = st.text_input("Source Place", value="", key="ov_src")
                override_dst = st.text_input("Destination Place", value="", key="ov_dst")
            with c2:
                override_budget = st.number_input("Budget Ceiling", min_value=0.0, value=0.0, step=500.0, key="ov_bdg")
                override_currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"], key="ov_cur")
            with c3:
                override_travelers = st.number_input("Travelers", min_value=1, value=1, key="ov_trv")
                override_days = st.number_input("Duration (Days)", min_value=1, value=2, key="ov_dys")

        if st.button("🚀 SYNTHESIZE & AUDIT TRAVEL PLAN", type="primary", use_container_width=True, key="btn_synthesize"):
            with st.spinner("Multi-Agent Graph executing: querying SerpApi, Tavily, YouTube, ORS, OpenWeather, and optimizing timetable..."):
                initial_state = create_initial_state(user_query=query_text)

                # Apply manual overrides if provided
                if override_src.strip():
                    initial_state["source"] = override_src.strip().title()
                if override_dst.strip():
                    initial_state["destination"] = override_dst.strip().title()
                if override_budget > 0:
                    initial_state["budget"] = float(override_budget)
                if override_currency:
                    initial_state["currency"] = override_currency
                if override_travelers > 1:
                    initial_state["travelers"] = override_travelers
                if override_days > 1:
                    initial_state["duration_days"] = override_days

                # Execute pipeline
                result_state = travel_pipeline.invoke(initial_state)

                st.session_state["travel_state"] = result_state
                st.session_state.pop("replan_banner", None)
                st.rerun()


def render_active_trip_dossier(state: TravelState, rag_service: TravelRAGService):
    """Renders the comprehensive travel dossier with horizontal website tabs."""
    src = state.get("source", "Origin")
    dst = state.get("destination", "Destination")
    days = state.get("duration_days", 2)
    budget = float(state.get("budget", 3000.0))
    cur = state.get("currency", "INR")
    bd = state.get("budget_breakdown")
    total_cost = bd.total_cost if bd else budget
    weather = state.get("weather")
    temp_str = f"{weather.temperature_c:.0f}°C • {weather.condition}" if weather else "Pleasant Weather"

    # Trip Dossier Banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
                border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 24px 28px; margin-bottom: 22px;
                box-shadow: 0 12px 36px -8px rgba(0, 0, 0, 0.5);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="font-size: 2.1rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">
                    🧭 {src} <span style="color: #38BDF8;">&rarr;</span> {dst}
                    <span style="font-size: 1rem; font-weight: 700; color: #94A3B8; margin-left: 10px; background: rgba(255,255,255,0.06); padding: 4px 12px; border-radius: 9999px;">
                        {days} Days
                    </span>
                </div>
                <div style="font-size: 0.95rem; color: #94A3B8; margin-top: 6px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                    <span>Total Grounded Cost: <b style="color: #38BDF8; font-size: 1.05rem;">{cur} {total_cost:,.0f}</b></span>
                    <span>•</span>
                    <span>Budget Ceiling: <b>{cur} {budget:,.0f}</b></span>
                    <span>•</span>
                    <span>Remaining Balance: <b style="color: #34D399; font-size: 1.05rem;">{cur} {max(0, budget - total_cost):,.0f}</b></span>
                    <span>•</span>
                    <span>⛅ {temp_str}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Ribbon: PDF Download & Modify Plan
    act_col1, act_col2 = st.columns([3, 2])
    with act_col1:
        try:
            pdf_bytes = generate_travel_pass_pdf(state)
            st.download_button(
                label="📥 Download Official Travel Pass (Printable PDF)",
                data=pdf_bytes,
                file_name=f"TravelPass_{src}_to_{dst}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Could not prepare PDF: {e}")

    with act_col2:
        with st.popover("✏️ Modify Query / Re-run Multi-Agent Planner", use_container_width=True):
            render_input_form(is_compact=True)

    # App-Style Top Horizontal Tabs
    tab_overview, tab_transit, tab_stays, tab_sights, tab_audit = st.tabs([
        "🧭 1. Trip Overview & Highlights",
        "🚆 2. Transit & Video Guides",
        "🏨 3. Stays, Homestays & Camps",
        "🗺️ 4. Sights & Time-Blocked Schedule",
        "📊 5. Budget, Safety & API Audit"
    ])

    # TAB 1: Overview
    with tab_overview:
        render_dashboard(state)

    # TAB 2: Transit
    with tab_transit:
        render_transport_view(state)

    # TAB 3: Stays
    with tab_stays:
        render_hotel_view(state)

    # TAB 4: Sights & Daily Schedule
    with tab_sights:
        sub_sights, sub_schedule = st.tabs([
            "📍 Top 10 Sights, Re-planning & Regional Food Guide",
            "📅 Daily Time-Blocked Schedule"
        ])
        with sub_sights:
            render_explore_places_view(state, rag_service)
        with sub_schedule:
            render_itinerary_view(state)

    # TAB 5: Budget & Audit
    with tab_audit:
        sub_budget, sub_safety, sub_audit, sub_trace = st.tabs([
            "💰 Itemized Budget Breakdown",
            "🛡️ Local Safety & Emergency Contacts",
            "🔍 Live Multi-API Quotas & Verification Audit",
            "🤖 LangGraph Agent Observability Trace"
        ])
        with sub_budget:
            render_budget_view(state)
        with sub_safety:
            render_local_services_view(state)
        with sub_audit:
            render_live_audit_view(state)
        with sub_trace:
            render_agent_trace_view(state)


if __name__ == "__main__":
    main()
