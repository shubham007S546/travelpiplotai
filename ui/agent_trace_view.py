"""Page 8 — Agent Observability & Execution Trace."""

import streamlit as st
import plotly.express as px
from models.travel_state import TravelState


def render_agent_trace_view(state: TravelState):
    st.header("Agent Observability & Telemetry Trace")
    st.caption("Detailed breakdown of agent durations, tool calls, and structured outputs.")

    logs = state.get("agent_logs", [])
    if not logs:
        st.info("No agent execution logs captured yet.")
        return

    # Latency Chart
    agent_names = [l.agent_name for l in logs]
    durations = [l.duration_ms for l in logs]

    fig = px.bar(
        x=durations,
        y=agent_names,
        orientation='h',
        labels={'x': 'Duration (ms)', 'y': 'Agent'},
        title="Agent Execution Latency Distribution",
        color=durations,
        color_continuous_scale="Viridis"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Agent Execution Log Matrix")
    for i, log in enumerate(logs):
        status_icon = "✓" if log.status == "completed" else "⚠"
        expander_title = f"{status_icon} [{log.agent_name}] — {log.duration_ms:.1f}ms | Confidence: {log.confidence * 100:.0f}%"

        with st.expander(expander_title, expanded=(log.status != "completed")):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"**Status:** `{log.status}`")
                st.markdown(f"**Started:** `{log.start_time}`")
                st.markdown(f"**Finished:** `{log.end_time}`")
                st.markdown(f"**Input:** {log.input_summary}")

            with c2:
                st.markdown(f"**Tool Calls ({len(log.tool_calls)}):**")
                if log.tool_calls:
                    for t in log.tool_calls:
                        st.code(t, language="bash")
                else:
                    st.write("Pure deterministic reasoning / state transformation")

            st.markdown(f"**Output Summary:**\n> {log.output_summary}")

            if log.errors:
                st.error("Errors encountered:\n" + "\n".join(log.errors))
