"""Page 5 — Chronological Day-by-Day Itinerary with Modern Schedule Aesthetics."""

import streamlit as st
from models.travel_state import TravelState
from services.trekking_service import TrekkingService


def render_itinerary_view(state: TravelState):
    itinerary = state.get("itinerary", [])
    cur = state.get("currency", "INR")
    dest = state.get("destination", "Destination")
    user_query = state.get("user_query", "")
    trek_intel = TrekkingService.get_trekking_intelligence(dest, query=user_query)

    # Header Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
                border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 22px 26px; margin-bottom: 24px;">
        <div style="font-size: 1.8rem; font-weight: 800; color: #F8FAFC;">📅 Time-Blocked Day-by-Day Travel Schedule for {dest}</div>
        <div style="font-size: 0.92rem; color: #94A3B8; margin-top: 4px;">
            Optimized chronological timeline ensuring non-overlapping activities, transit buffer windows, opening hours alignment, and meal stops.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not itinerary:
        st.info("Itinerary schedule not yet generated.")
        return

    for day in itinerary:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.6); padding: 14px 20px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2); margin: 18px 0 12px 0; display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 1.25rem; font-weight: 800; color: #38BDF8;">
                Day {day.day_number}: {day.theme}
            </div>
            <div style="font-size: 0.9rem; color: #CBD5E1; background: rgba(255,255,255,0.06); padding: 4px 12px; border-radius: 8px;">
                Est. Daily Spend: <b>{cur} {day.daily_cost:,.0f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # High-Altitude Trail Advisory
        is_trek_day = trek_intel and any(
            k in day.theme.lower() or any(k in it.title.lower() or k in it.location.lower() for it in day.items)
            for k in ("trek", "summit", "yulla", "lake", "climb", "mountain", "kanda", "bijli", "prashar")
        )
        if is_trek_day:
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3);
                        border-radius: 10px; padding: 12px 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.3rem;">🥾</span>
                <div>
                    <span style="font-weight: 800; color: #FBBF24;">Alpine Trail Advisory ({trek_intel['trek_name']}):</span>
                    <span style="color: #CBD5E1; font-size: 0.88rem;">
                        This trail climbs to {trek_intel['altitude_summit']}. Local guide & porter support is strongly recommended for navigation & safety.
                        Verified local guide contacts and camping gear tariffs are available under <b>Tab 5 (Safety & Trek Guides)</b>.
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        for item in day.items:
            # Color code based on item_type
            type_icons = {
                "travel": ("🚆 Transit Leg", "#38BDF8", "rgba(56, 189, 248, 0.15)"),
                "checkin": ("🏨 Stay Check-in", "#A78BFA", "rgba(167, 139, 250, 0.15)"),
                "dining": ("🍽️ Meal Stop", "#FBBF24", "rgba(251, 191, 36, 0.15)"),
                "attraction": ("📍 Sightseeing / Activity", "#34D399", "rgba(52, 211, 153, 0.15)"),
                "local_transit": ("🚌 Local Transit", "#60A5FA", "rgba(96, 165, 250, 0.15)"),
                "leisure": ("☕ Rest / Leisure", "#94A3B8", "rgba(148, 163, 184, 0.15)")
            }
            icon_label, text_col, bg_col = type_icons.get(item.item_type, ("• Activity", "#CBD5E1", "rgba(255,255,255,0.05)"))

            with st.container(border=True):
                col1, col2, col3 = st.columns([1.2, 3, 1])

                with col1:
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
                        <span style="font-size: 0.95rem; font-weight: 800; color: #F8FAFC;">{item.start_time} - {item.end_time}</span><br>
                        <span style="font-size: 0.75rem; color: #94A3B8;">{item.duration_mins} mins</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <span style="background: {bg_col}; color: {text_col}; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 700;">
                        {icon_label}
                    </span>
                    """, unsafe_allow_html=True)
                    st.markdown(f"**{item.title}**")
                    st.caption(f"📍 Location: {item.location}")
                    if item.travel_time_from_prev_mins > 0:
                        st.info(f"Transit: ~{item.travel_time_from_prev_mins} mins ({item.transport_mode or 'walking/local'})")
                    if item.notes:
                        st.caption(f"*{item.notes}*")

                with col3:
                    if item.estimated_cost > 0:
                        st.markdown(f"### {cur} {item.estimated_cost:,.0f}")
                    else:
                        st.markdown("<b style='color: #34D399;'>Free Public Access</b>", unsafe_allow_html=True)
                    if item.evidence:
                        st.caption(f"Source: {item.evidence.source}")
