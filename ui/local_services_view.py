"""Page 7 — Local Safety, Trekking Guides & Essential Services Directory with Modern Website Aesthetics."""

import streamlit as st
from models.travel_state import TravelState
from services.trekking_service import TrekkingService


def render_local_services_view(state: TravelState):
    dest = state.get("destination", "Destination")
    user_query = state.get("user_query", "")
    services = state.get("essential_services", [])
    trek_info = TrekkingService.get_trekking_intelligence(dest, query=user_query)

    # Header Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
                border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 22px 26px; margin-bottom: 24px;">
        <div style="font-size: 1.8rem; font-weight: 800; color: #F8FAFC;">🛡️ Safety Infrastructure & Verified Trekking Guides in {dest}</div>
        <div style="font-size: 0.92rem; color: #94A3B8; margin-top: 4px;">
            Verified mountain guide associations, camping logistics, agency contacts, 24/7 hospitals, police posts, and emergency helplines.
        </div>
    </div>
    """, unsafe_allow_html=True)

    gr = state.get("ground_reality")
    if not gr:
        from services.ground_reality_service import GroundRealityService
        res_dst = state.get("resolved_destination")
        res_src = state.get("resolved_source")
        forecast = state.get("weather")
        gr = GroundRealityService.generate_ground_reality_kit(res_dst, res_src, forecast)

    tab_reality, tab_guides, tab_emergency = st.tabs([
        "🎒 Common Traveler Ground Reality Field Kit",
        "🥾 Verified Local Trek Guides & Expedition Agencies",
        "🏥 24x7 Hospitals, Police Posts & Emergency Contacts"
    ])

    # ==========================================
    # TAB 1: GROUND REALITY & COMMON TRAVELER FIELD KIT
    # ==========================================
    with tab_reality:
        if gr:
            # Payment status badge styling
            pay_color = "#EF4444" if gr.digital_payment_status == "CASH_CRITICAL" else ("#F59E0B" if gr.digital_payment_status == "PARTIAL_UPI" else "#10B981")
            pay_bg = "rgba(239, 68, 68, 0.12)" if gr.digital_payment_status == "CASH_CRITICAL" else ("rgba(245, 158, 11, 0.12)" if gr.digital_payment_status == "PARTIAL_UPI" else "rgba(16, 185, 129, 0.12)")
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.9) 100%);
                        border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <span style="font-size: 1.3rem; font-weight: 800; color: #F8FAFC;">Ground Truth Field Kit for Everyday Travelers</span>
                        <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 2px;">
                            Zero-fluff ground intelligence on UPI outages, cash necessity, SIM connectivity drops, taxi tout defense, and motion sickness.
                        </div>
                    </div>
                    <span style="background: {pay_bg}; color: {pay_color}; border: 1px solid {pay_color};
                                padding: 6px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 800; letter-spacing: 0.04em;">
                        PAYMENT REALITY: {gr.digital_payment_status.replace('_', ' ')}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_fin, col_sim = st.columns(2)
            with col_fin:
                with st.container(border=True):
                    st.markdown("### 💵 Cash vs. UPI Ground Truth")
                    st.markdown(f"{gr.cash_guidance}")
                    st.markdown(f"💰 **Recommended Minimum Cash:** `₹{gr.recommended_cash_inr:.0f} per traveler` *(Carry small notes: ₹10, ₹20, ₹50, ₹100)*")
                    st.markdown(f"🏧 **Last Reliable ATM Hub:** `{gr.last_atm_hub}`")

            with col_sim:
                with st.container(border=True):
                    st.markdown("### 📶 Mobile Network & Signal Reality")
                    st.markdown(f"{gr.offline_readiness_warning}")
                    st.markdown("**Operator Field Status:**")
                    for net, status in gr.telecom_networks.items():
                        st.markdown(f"- **{net}:** `{status}`")

            col_luggage, col_tout = st.columns(2)
            with col_luggage:
                with st.container(border=True):
                    st.markdown("### 🎒 Luggage & Bag Drop Advisory")
                    st.markdown(f"{gr.luggage_cloakroom_info}")

            with col_tout:
                with st.container(border=True):
                    st.markdown("### 🚕 Taxi Tout Defense & Fair Tariffs")
                    st.markdown(f"{gr.anti_scam_transit_advice}")
                    st.info(f"💡 **Statutory Benchmark:** {gr.statutory_fare_tip}")

            col_health, col_tips = st.columns(2)
            with col_health:
                with st.container(border=True):
                    st.markdown("### 🤢 Motion Sickness & Mountain Health")
                    st.markdown(f"{gr.health_motion_sickness_advice}")
                    if gr.altitude_ams_risk:
                        st.warning("⚠️ **High Altitude AMS Warning:** Destination exceeds 2,500m. Avoid rapid ascents and stay hydrated.")

            with col_tips:
                with st.container(border=True):
                    st.markdown("### 🧥 Gear, Power & Family Travel Tips")
                    st.markdown(f"**Clothing & Power:** {gr.clothing_and_power_advice}")
                    st.markdown(f"**Family & Safety:** {gr.women_and_family_tips}")

            if gr.packing_checklist:
                with st.container(border=True):
                    st.markdown("### 📋 Essential Field Packing Checklist")
                    st.caption("Check off items before leaving your origin:")
                    cols_chk = st.columns(2)
                    for idx, item in enumerate(gr.packing_checklist):
                        with cols_chk[idx % 2]:
                            st.checkbox(item, key=f"gr_chk_{idx}")

    # ==========================================
    # TAB 2: TREK GUIDES & EXPEDITION AGENCIES
    # ==========================================
    with tab_guides:
        if trek_info:
            # Alpine Trail Alert Banner
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
                        border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 20px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                    <span style="font-size: 1.5rem;">🏔️</span>
                    <span style="font-size: 1.3rem; font-weight: 800; color: #38BDF8;">{trek_info['trek_name']}</span>
                    <span style="background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3);
                                padding: 3px 10px; border-radius: 9999px; font-size: 0.76rem; font-weight: 700;">
                        {trek_info['difficulty']}
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-top: 14px;">
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                        <div style="font-size: 0.72rem; color: #94A3B8;">SUMMIT ALTITUDE</div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC;">{trek_info['altitude_summit']}</div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                        <div style="font-size: 0.72rem; color: #94A3B8;">TRAILHEAD / BASE</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC;">{trek_info['base_village']}</div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                        <div style="font-size: 0.72rem; color: #94A3B8;">DURATION & DISTANCE</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC;">{trek_info['trek_duration']} • {trek_info['trail_distance']}</div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                        <div style="font-size: 0.72rem; color: #94A3B8;">BEST CLIMBING SEASON</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC;">{trek_info['best_season']}</div>
                    </div>
                </div>
                <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; padding: 10px 14px; border-radius: 6px; margin-top: 14px; font-size: 0.86rem; color: #CBD5E1;">
                    ⚠️ <b>Why a Certified Local Guide is Mandatory:</b> {trek_info['why_guide_needed']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Verified Agencies & Guide Unions
            st.markdown("### 🧑‍🤝‍🧑 Verified Local Guide Associations & Expedition Agencies")
            st.caption("Direct, un-intermediated contacts for local guide welfare unions and licensed Himalayan expedition agencies.")

            guide_cols = st.columns(len(trek_info["verified_agencies"]))
            for idx, ag in enumerate(trek_info["verified_agencies"]):
                with guide_cols[idx]:
                    with st.container(border=True):
                        # Badges
                        badge_html = "".join([
                            f'<span style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.25); padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 700; margin-right: 4px; display: inline-block; margin-bottom: 4px;">{b}</span>'
                            for b in ag["badges"]
                        ])
                        st.markdown(badge_html, unsafe_allow_html=True)
                        st.markdown(f"#### {ag['name']}")
                        st.markdown(f"📍 **Base:** `{ag['base_location']}`")
                        st.write(ag["services_offered"])

                        st.markdown("##### 📞 Direct Verified Contacts:")
                        for ph in ag["phones"]:
                            clean_ph = ph.replace(" ", "").replace("-", "")
                            st.markdown(f"• 📱 **Call:** [`{ph}`](tel:{clean_ph})")
                        if ag.get("whatsapp"):
                            wa_clean = ag['whatsapp'].replace("+", "").replace(" ", "").replace("-", "")
                            st.markdown(f"""
                            <a href="https://wa.me/{wa_clean}" target="_blank" style="display: inline-block; background: #25D366; color: white; padding: 6px 14px; border-radius: 8px; text-decoration: none; font-size: 0.82rem; font-weight: 700; margin-top: 6px;">
                                💬 WhatsApp Chat with Agency
                            </a>
                            """, unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("##### 🏷️ Standard Union Tariffs:")
                        for k, v in ag["pricing"].items():
                            label = k.replace("_", " ").title()
                            st.markdown(f"• **{label}:** `{v}`")

            st.markdown("<br>", unsafe_allow_html=True)

            # Facilities Provided Checklist
            st.markdown("### ⛺ Complete Trekking Facilities Provided by Agencies")
            st.caption("Standard equipment and logistical services provided for mountain treks like Yulla Kanda:")

            fac_cols = st.columns(2)
            for f_idx, fac in enumerate(trek_info["facilities_provided"]):
                with fac_cols[f_idx % 2]:
                    with st.container(border=True):
                        st.markdown(f"#### {fac['icon']} {fac['name']}")
                        st.write(fac["details"])
                        st.caption(f"Status: **{fac['tier']}**")

            # High Altitude Safety Protocol
            with st.expander("🩺 High-Altitude Acclimatization & Safety Rules (AMS Protocol)", expanded=False):
                for rule in trek_info["safety_protocol"]:
                    st.markdown(f"• {rule}")
        else:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 20px;">
                <div style="font-size: 1.2rem; font-weight: 700; color: #F8FAFC;">🗺️ Certified Tourism Guides for {dest}</div>
                <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 6px;">
                    For cultural walking tours, heritage walks, and local sightseeing in {dest}, verified regional guides licensed by the
                    <b>Ministry of Tourism (Incredible India)</b> and State Tourism Development Corporation are stationed at major heritage ticket counters.
                </div>
                <div style="margin-top: 14px; font-size: 0.85rem; color: #CBD5E1;">
                    • <b>Standard Full-Day Tour Guide Tariff:</b> ₹1,200 – ₹1,800 / day (approved government rates)<br>
                    • <b>Half-Day Heritage Walk Tariff:</b> ₹700 – ₹1,000<br>
                    • <b>Tourist Helpline:</b> 1363 (Toll-Free 24x7 Multilingual Guide Assistance)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================
    # TAB 2: EMERGENCY MEDICAL, POLICE & ATMS
    # ==========================================
    with tab_emergency:
        if not services:
            st.info(f"No emergency services cataloged for {dest}.")
        else:
            # Category filters
            col_filter, col_search = st.columns([2, 2])
            with col_filter:
                service_types = ["All Categories"] + sorted(list(set(s.service_type.value.replace("_", " ").title() for s in services)))
                selected_type = st.selectbox("Filter by Infrastructure Category", service_types, key="sel_infra_cat")

            filtered_services = services
            if selected_type != "All Categories":
                filtered_services = [s for s in services if s.service_type.value.replace("_", " ").title() == selected_type]

            cols = st.columns(2)
            for i, s in enumerate(filtered_services):
                with cols[i % 2]:
                    with st.container(border=True):
                        is_emerg = s.is_24x7 or "hospital" in s.service_type.value.lower() or "police" in s.service_type.value.lower()
                        badge_bg = "rgba(239, 68, 68, 0.15)" if is_emerg else "rgba(56, 189, 248, 0.15)"
                        badge_color = "#F87171" if is_emerg else "#38BDF8"
                        badge_border = "rgba(239, 68, 68, 0.3)" if is_emerg else "rgba(56, 189, 248, 0.3)"
                        badge_text = "🚨 24x7 EMERGENCY" if s.is_24x7 else "🕒 BUSINESS HOURS"

                        st.markdown(f"""
                        <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border};
                                    padding: 3px 10px; border-radius: 9999px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em;">
                            {s.service_type.value.replace('_', ' ').upper()} • {badge_text}
                        </span>
                        """, unsafe_allow_html=True)

                        st.markdown(f"### {s.name}")
                        st.markdown(f"📍 **Address:** {s.address} `({s.distance_km:.1f} km away)`")
                        if s.phone:
                            st.markdown(f"📞 **Phone / Emergency Helpline:** `{s.phone}`")
                        st.markdown(f"🟢 **Status:** `{s.opening_status}`")
                        st.caption(f"Source: {s.evidence.source} ({s.evidence.tier.value.split(':')[0]})")

