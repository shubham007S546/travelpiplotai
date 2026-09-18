"""Page 4 — Accommodation & Lodging Options with Modern Booking Portal Aesthetics."""

import streamlit as st
from models.travel_state import TravelState


def render_hotel_view(state: TravelState):
    dest = state.get("destination", "Destination")
    cur = state.get("currency", "INR")
    stays = state.get("hotel_options", [])
    sel_stay = state.get("selected_hotel")

    # Header Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
                border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 22px 26px; margin-bottom: 24px;">
        <div style="font-size: 1.8rem; font-weight: 800; color: #F8FAFC;">🏨 Verified Accommodations & Mountain Camps in {dest}</div>
        <div style="font-size: 0.92rem; color: #94A3B8; margin-top: 4px;">
            Grounded lodging options cross-checked via <b>SerpApi Google Hotels</b>, local homestay directories, and official tourism rate cards.
            Includes budget homestays, verified tent rentals, check-in/out policies, and included gear.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if sel_stay:
        stay_title = "⭐ Recommended Stay" if not sel_stay.is_camping else "⛺ Recommended Campsite & Tent Rental"
        st.subheader(stay_title)
        
        with st.container(border=True):
            img_c, info_c, rate_c = st.columns([1.2, 2.2, 1])
            
            with img_c:
                stay_img = getattr(sel_stay, "image_url", None)
                if stay_img:
                    try:
                        st.image(stay_img, use_container_width=True)
                    except Exception:
                        pass
                else:
                    b_icon = ">" if sel_stay.is_camping else "🏨"
                    b_label = "VERIFIED CAMPSITE" if sel_stay.is_camping else "VERIFIED LODGING"
                    st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.45); border: 1px dashed rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 20px 10px; text-align: center;">
                        <span style="font-size: 1.8rem;">{b_icon}</span>
                        <div style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; margin-top: 4px;">{b_label}</div>
                        <div style="font-size: 0.7rem; color: #94A3B8;">Direct ground booking • No stock photos</div>
                    </div>
                    """, unsafe_allow_html=True)

            with info_c:
                if sel_stay.is_camping:
                    st.markdown("""
                    <span style="background: rgba(16, 185, 129, 0.18); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4);
                                padding: 4px 12px; border-radius: 9999px; font-size: 0.76rem; font-weight: 700; letter-spacing: 0.04em;">
                        ⛺ MOUNTAIN CAMPSITE & TENT RENTAL VERIFIED
                    </span>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <span style="background: rgba(56, 189, 248, 0.18); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4);
                                padding: 4px 12px; border-radius: 9999px; font-size: 0.76rem; font-weight: 700; letter-spacing: 0.04em;">
                        ✓ VERIFIED OPTIMAL LODGING
                    </span>
                    """, unsafe_allow_html=True)

                st.markdown(f"### {sel_stay.name}")
                st.caption(f"Category: **{sel_stay.stay_type.value.title()}** | 📍 {sel_stay.address}")
                
                stars = "★" * int(sel_stay.rating) + "☆" * (5 - int(sel_stay.rating))
                st.markdown(f"<span style='color: #FBBF24; font-size: 1.1rem;'>{stars}</span> &nbsp;<b>{sel_stay.rating:.1f}/5.0</b> <span style='color: #94A3B8;'>({sel_stay.reviews_count} verified reviews)</span>", unsafe_allow_html=True)
                
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown(f"📍 **Distance to Center / Trailhead:** `{sel_stay.distance_to_center_km:.1f} km`")
                with c_b:
                    st.markdown(f"🕒 **Check-in / Out:** `{sel_stay.check_in_time}` ➔ `{sel_stay.check_out_time}`")

                if sel_stay.is_camping and sel_stay.gear_included:
                    st.markdown("**🎒 Equipment Included with Rental:**")
                    gear_badges = " ".join([f"<span style='background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; margin-right: 6px; border: 1px solid rgba(255,255,255,0.08);'>{g}</span>" for g in sel_stay.gear_included])
                    st.markdown(gear_badges, unsafe_allow_html=True)
                    if sel_stay.pitch_fee:
                        st.caption(f"💡 *Bringing your own tent• Ground pitch fee is only ₹{sel_stay.pitch_fee:.0f}/night.*")

                st.markdown("**s Property Amenities:**")
                amenity_badges = " ".join([f"<span style='background: rgba(30, 41, 59, 0.7); padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; margin-right: 6px; border: 1px solid rgba(255,255,255,0.08);'>✓ {a}</span>" for a in sel_stay.amenities])
                st.markdown(amenity_badges, unsafe_allow_html=True)

            with rate_c:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.7); padding: 18px 14px; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.08); text-align: center;">
                    <div style="font-size: 0.78rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Nightly Rate</div>
                    <div style="font-size: 1.9rem; font-weight: 800; color: #38BDF8; margin: 4px 0;">{cur} {sel_stay.price_per_night:,.0f}</div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">{'tent & gear rental' if sel_stay.is_camping else 'per room per night'}</div>
                    <div style="margin-top: 12px; padding: 4px 8px; background: rgba(16, 185, 129, 0.15); border-radius: 6px; color: #34D399; font-size: 0.75rem; font-weight: 700;">
                        ✓ Grounded Tariff
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"Source: {sel_stay.evidence.source if sel_stay.evidence else sel_stay.source}")
                if sel_stay.booking_url:
                    st.link_button("🌐 Open Booking / Contact", sel_stay.booking_url, use_container_width=True)

    st.markdown("---")
    st.subheader(f"All Evaluated Stays & Alternatives in {dest}")
    if stays:
        alt_cols = st.columns(min(len(stays), 3))
        for idx, s in enumerate(stays):
            if sel_stay and s.id == sel_stay.id:
                continue
            with alt_cols[idx % len(alt_cols)]:
                with st.container(border=True):
                    alt_img = getattr(s, "image_url", None)
                    if alt_img:
                        try:
                            st.image(alt_img, use_container_width=True)
                        except Exception:
                            pass
                    else:
                        alt_icon = ">" if s.is_camping else "🏨"
                        st.markdown(f"""
                        <div style="background: rgba(30, 41, 59, 0.45); border: 1px dashed rgba(56, 189, 248, 0.25); border-radius: 10px; padding: 14px; text-align: center; margin-bottom: 10px;">
                            <span style="font-size: 1.4rem;">{alt_icon}</span>
                            <div style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; margin-top: 2px;">VERIFIED PROPERTY</div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown(f"#### {s.name}")
                    st.caption(f"{s.stay_type.value.title()} • {s.address}")
                    st.markdown(f"**Rating:** ★ `{s.rating:.1f}/5.0` &nbsp;|&nbsp; `{s.distance_to_center_km:.1f} km away`")
                    st.markdown(f"### {cur} {s.price_per_night:,.0f} <span style='font-size:0.8rem; color:#94A3B8;'>/ night</span>", unsafe_allow_html=True)
                    st.caption(f"Source: {s.evidence.source}")
                    if s.booking_url:
                        st.link_button("View Property", s.booking_url, use_container_width=True)
    else:
        st.info("No alternative accommodations recorded.")
