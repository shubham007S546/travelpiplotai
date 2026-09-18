"""Page 3 — Intercity Transport Options, Fare Transparency & Route Audits with Modern Travel Portal Aesthetics."""

import streamlit as st
from models.travel_state import TravelState
from models.transport import TransportOption
from services.youtube_service import YouTubeTravelService


def render_transport_card(opt: TransportOption, is_selected: bool, cur: str = "INR", is_outbound: bool = True):
    """Renders a verified transport card with multi-leg breakdown, interchange badges, and tariff expanders."""
    with st.container(border=True):
        if is_selected:
            st.markdown("""
            <div style="margin-bottom: 8px;">
                <span style="background: rgba(16, 185, 129, 0.18); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4);
                            padding: 4px 12px; border-radius: 9999px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.04em;">
                    ✓ SELECTED / RECOMMENDED OPTION
                </span>
            </div>
            """, unsafe_allow_html=True)

        mode_emoji = {
            "bus": "🚌",
            "train": "🚆",
            "taxi": "🚕",
            "flight": "✈️",
            "walking": "🥾"
        }.get(opt.mode.value.lower(), "🚗")

        st.markdown(f"### {mode_emoji} {opt.provider}")
        
        dur_hrs = opt.duration // 60
        dur_mins = opt.duration % 60
        dur_display = f"{dur_hrs}h {dur_mins:02d}m" if dur_hrs > 0 else f"{dur_mins}m"
        st.caption(f"Mode: **{opt.mode.value.title()}** &nbsp;|&nbsp; Duration: **{dur_display}** &nbsp;|&nbsp; Distance: **{opt.distance_km:.1f} km**")
        
        # Schedule time display
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.6); padding: 12px 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">DEPARTURE</span><br>
                    <b style="font-size: 1.15rem; color: #F8FAFC;">{opt.departure}</b><br>
                    <span style="font-size: 0.82rem; color: #CBD5E1;">{opt.origin}</span>
                </div>
                <div style="color: #38BDF8; font-size: 1.4rem; padding: 0 10px;">&rarr;</div>
                <div style="text-align: right;">
                    <span style="font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">ARRIVAL</span><br>
                    <b style="font-size: 1.15rem; color: #F8FAFC;">{opt.arrival}</b><br>
                    <span style="font-size: 0.82rem; color: #CBD5E1;">{opt.destination}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Fare Display
        if opt.fare is not None:
            badge_type = opt.fare_type or "OFFICIAL_TARIFF"
            badge_color = "🟢" if badge_type in ("LIVE", "OFFICIAL_TARIFF") else ("🟡" if badge_type == "ESTIMATED" else "⚪")
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 12px 0 8px 0;
                        background: rgba(30, 41, 59, 0.4); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                <div>
                    <span style="font-size: 1.8rem; font-weight: 800; color: #38BDF8;">₹{opt.fare:,.0f}</span>
                    <span style="font-size: 0.82rem; color: #94A3B8;">/ person</span>
                </div>
                <div>
                    <span style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; color: #7DD3FC; font-weight: 600;">
                        {badge_color} {badge_type.replace('_', ' ')}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("## *Fare on Board*")

        # Multi-Leg Step-by-Step Visual Timeline
        if opt.is_multi_leg and opt.legs:
            st.markdown("---")
            st.markdown("#### 🔄 Multi-Hop Route Decomposition:")
            for idx, leg in enumerate(opt.legs, 1):
                leg_fare_str = f"₹{leg.fare:.0f}" if leg.fare is not None and leg.fare > 0 else ("Free (Mountain Trek)" if leg.fare == 0 else "Fare on board")
                m_icon = "🚌" if leg.mode.value == "bus" else ("🥾" if leg.mode.value == "walking" else "🚕")
                
                transfer_badge = ""
                if idx < len(opt.legs):
                    transfer_badge = f"<div style='margin-left: 20px; font-size: 0.75rem; color: #F59E0B; padding: 2px 0;'>🔄 <i>Transfer / Bus Interchange (~25 min buffer)</i></div>"

                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.4); border-left: 3px solid #38BDF8; padding: 8px 12px; border-radius: 0 8px 8px 0; margin-bottom: 6px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #F1F5F9; font-size: 0.88rem;">{idx}. {m_icon} {leg.origin} &rarr; {leg.destination}</span>
                        <span style="font-weight: 700; color: #34D399; font-size: 0.85rem;">{leg_fare_str}</span>
                    </div>
                    <div style="font-size: 0.76rem; color: #94A3B8; margin-top: 2px;">
                        `{leg.provider}` • `{leg.distance_km:.1f} km` • `{leg.duration} mins`
                    </div>
                </div>
                {transfer_badge}
                """, unsafe_allow_html=True)

        if opt.booking_url:
            st.link_button("🌐 View Official Timetable / Booking", opt.booking_url, use_container_width=True)

        # "WHY THIS FARE•" Expander
        with st.expander("💡 WHY THIS FARE•"):
            if opt.fare is not None and opt.fare_model_details:
                details = opt.fare_model_details
                st.markdown(f"- **Road Distance:** `{opt.distance_km:.1f} km`")
                st.markdown(f"- **Fare Source:** {details.get('tariff_source', 'Official Published State Transport Tariff')}")
                if "base_fare" in details and "per_km_rate" in details:
                    st.markdown(f"- **Fare Model:** ₹{details['base_fare']:.0f} base + ₹{details['per_km_rate']:.2f}/km")
                    st.markdown(f"- **Calculation:** {details.get('formula', 'base + rate*km')} = **₹{opt.fare:.0f}**")
                else:
                    st.markdown(f"- **Calculation Breakdown:** {details.get('formula', details.get('breakdown', f'₹{opt.fare:.0f}'))}")
                st.markdown(f"- **Final Verified Fare:** **₹{opt.fare:.0f}**")
            elif opt.fare is not None:
                st.markdown(f"- **Fare:** ₹{opt.fare:.0f}")
                st.markdown(f"- **Source:** {opt.evidence.source if opt.evidence else 'Verified Tariff'}")
                st.markdown(f"- **Type:** `{opt.fare_type}`")
            else:
                st.info("Exact fare varies locally; confirm on board.")

        # "WHY THIS ROUTE•" Expander
        with st.expander("🗺️ WHY THIS ROUTE•"):
            routes = opt.route_details or {}
            engine = routes.get("routing_engine", "OpenRouteService / OSRM")
            st.markdown(f"- **Routing Engine:** `{engine}`")
            st.markdown(f"- **Total Transit Distance:** `{opt.distance_km:.1f} km`")
            st.markdown(f"- **Total Estimated Duration:** `{dur_display}`")
            rationale = routes.get("rationale", "Selected for lowest transit cost, verified public bus availability, and mountain terrain safety.")
            st.markdown(f"- **Rationale:** {rationale}")
            if opt.is_multi_leg:
                st.info("🔄 **Route Topology**: Multi-Hop Connecting Public Transit with intermediate transfer stands.")


def render_transport_view(state: TravelState):
    src = state.get("source", "Origin")
    dst = state.get("destination", "Destination")
    cur = state.get("currency", "INR")

    outbound = state.get("outbound_transport_options", [])
    returns = state.get("return_transport_options", [])
    sel_out = state.get("selected_outbound_transport")
    sel_ret = state.get("selected_return_transport")

    # Header Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
                border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 22px 26px; margin-bottom: 24px;">
        <div style="font-size: 1.8rem; font-weight: 800; color: #F8FAFC;">🚆 Intercity & Regional Ground Mobility: {src} ➔ {dst}</div>
        <div style="font-size: 0.92rem; color: #94A3B8; margin-top: 4px;">
            Verified public state carriage buses, express coaches, shared mountain sumos, trains, and verified routes.
            Calculated via <b>OpenRouteService / OSRM</b> road network matrices with deterministic tariff formulas.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Proactive Trip Disruption & Hazard Alert Banner
    disruption_alerts = state.get("disruption_alerts", [])
    has_disruption = state.get("has_disruption_risk", False)
    recommended_reroute = state.get("recommended_reroute")

    if has_disruption and disruption_alerts:
        top_alert = disruption_alerts[0]
        alert_title = top_alert.get("title", "⚠️ Active Transit Hazard Advisory")
        alert_desc = top_alert.get("description", "")
        alert_action = top_alert.get("action_required", "")
        reroute_text = recommended_reroute or alert_action
        reroute_html = f"<div style='margin-top: 8px; padding-top: 8px; border-top: 1px dashed rgba(245, 158, 11, 0.4); font-size: 0.88rem; color: #FDE68A;'><b>Recommended Bypass Corridor:</b> {reroute_text}</div>" if reroute_text else ""

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.18) 0%, rgba(180, 83, 9, 0.28) 100%);
                    border: 1px solid #F59E0B; border-radius: 14px; padding: 18px 24px; margin-bottom: 22px; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.15);">
            <div style="display: flex; align-items: flex-start; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; color: #FBBF24; font-size: 1.15rem; font-weight: 700;">
                        {alert_title}
                    </h4>
                    <p style="margin: 6px 0 0 0; color: #FEF3C7; font-size: 0.92rem; line-height: 1.45;">
                        {alert_desc}
                    </p>
                    {reroute_html}
                </div>
                <div style="font-size: 1.8rem; margin-left: 16px;">🚨</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Smart Contextual Transit Notice
    src_lower = src.lower()
    # Determine if origin city has rideshare / is urban
    urban_origins = ["delhi", "chandigarh", "mumbai", "bangalore", "amritsar", "jaipur", "dehradun", "haridwar", "shimla"]
    is_urban_origin = any(city in src_lower for city in urban_origins)
    is_hill_destination = any(x in state.get("destination", "").lower() for x in ["manali", "kullu", "kasol", "mandi", "sundernagar", "kinnaur", "spiti", "lahaul", "tosh", "kheerganga", "jibhi", "tirthan", "prashar", "yulla"])

    if is_urban_origin:
        st.info(
            f"🏙️ **Urban Origin Notice ({src})**: App-based rideshare (**Uber, Ola, Rapido**) is available for your local city pickup. "
            "However, once you enter the **Himachal Pradesh hill valleys**, rideshare apps do **NOT** operate. "
            "Beyond the plains corridor, transit relies on **HRTC state buses, HRTC Volvo semi-deluxe, shared maxi-cabs**, and **local taxi unions**."
        )
    elif is_hill_destination:
        st.info(
            "🏔️ **Grounded Regional Transit Notice**: App-based taxi aggregators (**Uber, Ola, Rapido**) do NOT operate in Himachal hill valleys and rural blocks. "
            "Verified ground mobility relies on **HRTC state carriage buses, HRTC Volvo semi-deluxe coaches, local shared maxi-cabs (Tata Sumo/Bolero), registered taxi unions**, and traditional mountain foot trails."
        )
    else:
        st.info(
            "🚌 **Transit Verification Notice**: All transport options below are verified against HRTC gazette tariffs, "
            "routing APIs, and ground-truth mountain trail data. Fares are per-person unless noted."
        )

    # Conflict banner if detected
    if state.get("distance_status") == "CONFLICT":
        st.warning(
            f"⚠️ **DATA CONFLICT DETECTED**: Routing providers report a {state.get('distance_difference_pct', 0):.1f}% divergence in road distance. "
            "Please verify destination locality if unexpected."
        )

    # 💰 Cost Savings Banner
    savings_out = state.get("cheapest_outbound_savings_vs_expensive", 0)
    taxi_out_fare = state.get("taxi_outbound_fare", 0)
    sel_out_fare = sel_out.price if sel_out else None
    if savings_out and savings_out >= 150 and sel_out_fare is not None:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.18) 0%, rgba(5, 150, 105, 0.28) 100%);
                    border: 1px solid #10B981; border-radius: 14px; padding: 16px 24px; margin-bottom: 20px;
                    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.12);">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 2rem;">🪙</div>
                <div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #34D399;">
                        Save ₹{savings_out:,.0f} by choosing the cheapest public option!
                    </div>
                    <div style="font-size: 0.88rem; color: #6EE7B7; margin-top: 2px;">
                        Cheapest verified transit: <b>₹{sel_out_fare:,.0f}</b> &nbsp;|&nbsp; 
                        Most expensive (private taxi): <b>₹{taxi_out_fare:,.0f}</b> &nbsp;|&nbsp;
                        <b>₹{savings_out:,.0f} saved</b> by taking public bus 🚌
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader(f"Outbound Journey: {src} ➔ {dst}")
    if outbound:
        # Sort by price (cheapest first)
        outbound_sorted = sorted(outbound, key=lambda o: o.price)
        cols = st.columns(min(len(outbound_sorted), 3))  # max 3 columns to avoid cramped layout
        for i, opt in enumerate(outbound_sorted):
            with cols[i % len(cols)]:
                is_selected = sel_out and sel_out.id == opt.id
                render_transport_card(opt, is_selected, cur)
    else:
        st.info("No outbound transit options verified for this route.")

    st.markdown("---")

    st.subheader(f"Return Journey: {dst} ➔ {src}")
    if returns:
        returns_sorted = sorted(returns, key=lambda o: o.price)
        cols_ret = st.columns(min(len(returns_sorted), 3))
        for i, opt in enumerate(returns_sorted):
            with cols_ret[i % len(cols_ret)]:
                is_selected = sel_ret and sel_ret.id == opt.id
                render_transport_card(opt, is_selected, cur)
    else:
        st.info("No return transit options verified for this route.")

    st.markdown("---")

    # YouTube Ground-Truth Travel Vlogs with Timeline Audit
    st.subheader("📹 Real Traveler Video Evidence & Timeline Audit (YouTube)")
    st.caption("Live traveler vlogs cross-checking fares, road conditions, and trek difficulty. Older guides include inflation adjustment notes.")

    yt_service = YouTubeTravelService()
    if yt_service.is_available():
        vlogs = yt_service.search_travel_vlogs(src, dst, max_results=3)
        if vlogs:
            v_cols = st.columns(len(vlogs))
            for i, v in enumerate(vlogs):
                with v_cols[i]:
                    with st.container(border=True):
                        st.image(v["thumbnail_url"], use_container_width=True)
                        st.markdown(f"**[{v['title']}]({v['video_url']})**")
                        st.caption(f"👤 {v['channel']} | 📅 Published: **{v['published_date_formatted']}**")
                        st.markdown(f"**Timeline Status:** {v['freshness_badge']}")
                        st.caption(f"ℹ️ {v['fare_note']}")
                        st.link_button("- Watch Guide on YouTube", v["video_url"], use_container_width=True)
        else:
            st.info(f"No traveler vlogs retrieved for {src} to {dst}.")
    else:
        st.caption("Add YOUTUBE_API_KEY to view real traveler video guides.")
