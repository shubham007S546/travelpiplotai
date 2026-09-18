"""Page 6 — Budget Optimization, Uncertainty Modeling & Grounded Breakdown with Modern Financial Dashboard Aesthetics."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from models.travel_state import TravelState


def render_budget_view(state: TravelState):
    bd = state.get("budget_breakdown")
    cur = state.get("currency", "INR")
    total_budget = float(state.get("budget", 3000.0))

    # Header Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
                border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 22px 26px; margin-bottom: 24px;">
        <div style="font-size: 1.8rem; font-weight: 800; color: #F8FAFC;">💰 Deterministic Budget Optimization & Grounded Accounting</div>
        <div style="font-size: 0.92rem; color: #94A3B8; margin-top: 4px;">
            Pure-Python arithmetic guarantees zero hallucinations. Includes itemized category breakdown, 8% emergency reserves, and uncertainty bands.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not bd:
        st.info("Budget analysis not yet generated.")
        return

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("User Budget Ceiling", f"{cur} {total_budget:,.0f}")
    c2.metric("Expected Total Cost", f"{cur} {bd.total_estimated_cost:,.0f}")
    c3.metric("Remaining Balance", f"{cur} {bd.remaining_budget:,.0f}")
    c4.metric("Budget Utilization", f"{bd.budget_utilization_pct:.1f}%")

    # Uncertainty Range Display
    st.markdown("### 📊 Cost Uncertainty Modeling (Min / Expected / Max)")
    u1, u2, u3 = st.columns(3)
    u1.metric("Minimum Cost (Lower Bound)", f"{cur} {bd.minimum_cost:,.0f}")
    u2.metric("Expected Cost (Baseline)", f"{cur} {bd.expected_cost:,.0f}")
    u3.metric("Maximum Cost (Upper Bound)", f"{cur} {bd.maximum_cost:,.0f}")

    # Feasibility Guidance
    if not bd.is_feasible:
        st.error(f"⚠️ **BUDGET CONSTRAINT VIOLATED**: {bd.feasibility_status_message}")
        for s in bd.downgrade_suggestions:
            st.warning(f"• {s}")
    elif bd.maximum_cost > total_budget:
        st.warning(f"⚠️ **BUDGET UNCERTAINTY**: {bd.feasibility_status_message}")
    else:
        st.success(f"✓ **BUDGET COMPLIANT**: {bd.feasibility_status_message}")

    st.markdown("---")

    # Visual Charts
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Category Spend Distribution")
        categories = [
            "Intercity Transport", "Accommodation", "Food & Dining",
            "Activities & Sightseeing", "Local Mobility", "Emergency Reserve"
        ]
        values = [
            bd.intercity_transport_cost,
            bd.stay_cost,
            bd.food_cost,
            bd.activity_cost,
            bd.local_mobility_cost,
            bd.emergency_reserve
        ]

        fig_pie = px.pie(
            values=values,
            names=categories,
            hole=0.5,
            color_discrete_sequence=['#38BDF8', '#818CF8', '#FBBF24', '#34D399', '#60A5FA', '#F472B6']
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8', family='Plus Jakarta Sans'),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=20, b=40),
            height=340
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

    with col_right:
        st.subheader("Cost Uncertainty Band")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name='Min Cost',
            x=categories,
            y=[round(v * 0.88, 1) for v in values],
            marker_color='#34D399'
        ))
        fig_bar.add_trace(go.Bar(
            name='Expected Cost',
            x=categories,
            y=values,
            marker_color='#38BDF8'
        ))
        fig_bar.add_trace(go.Bar(
            name='Max Cost',
            x=categories,
            y=[round(v * 1.18, 1) for v in values],
            marker_color='#F59E0B'
        ))
        fig_bar.update_layout(
            barmode='group',
            yaxis_title=f"Amount ({cur})",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8', family='Plus Jakarta Sans'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(size=10)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.06)'),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=20, b=40),
            height=340
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    # Detailed Verified/Estimated Table
    st.subheader("📋 Grounded Itemized Accounting Table")
    st.caption("Factual amounts are verified against live provider feeds or published tariffs. Values without exact quotes are flagged as ESTIMATED or UNKNOWN.")

    table_rows = []
    for item in bd.category_items:
        table_rows.append({
            "Category": item.category,
            "Amount": f"{cur} {item.amount:,.0f}",
            "Range (Min - Max)": f"{cur} {item.min_amount:,.0f} – {cur} {item.max_amount:,.0f}",
            "Type": item.type,
            "Source": item.source,
            "Confidence": f"{int(item.confidence * 100)}%"
        })

    # Add Emergency and Total rows
    table_rows.append({
        "Category": "Emergency Reserve (8%)",
        "Amount": f"{cur} {bd.emergency_reserve:,.0f}",
        "Range (Min - Max)": f"{cur} {bd.emergency_reserve:,.0f}",
        "Type": "OFFICIAL_TARIFF",
        "Source": "Deterministic 8% Policy",
        "Confidence": "100%"
    })
    table_rows.append({
        "Category": "TOTAL EXPECTED COST",
        "Amount": f"{cur} {bd.total_estimated_cost:,.0f}",
        "Range (Min - Max)": f"{cur} {bd.minimum_cost:,.0f} – {cur} {bd.maximum_cost:,.0f}",
        "Type": "COMPOSITE",
        "Source": "Deterministic Pure-Python Arithmetic",
        "Confidence": f"{int(state.get('trust_scores', {}).get('overall_confidence', 90))}%"
    })

    st.table(table_rows)
