"""TravelPilot AI — ElevenLabs Conversational Voice Agent Integration."""

import os
import streamlit as st
import streamlit.components.v1 as components

# Default Agent ID provided by user
DEFAULT_ELEVENLABS_AGENT_ID = "agent_6101m2taekate5zszyzp2r1fsbf2"


def get_elevenlabs_agent_id() -> str:
    """Retrieves the ElevenLabs Agent ID from env, secrets, or fallback default."""
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    if not agent_id and hasattr(st, "secrets"):
        agent_id = st.secrets.get("ELEVENLABS_AGENT_ID")
    return (agent_id or DEFAULT_ELEVENLABS_AGENT_ID).strip()


def render_elevenlabs_widget(height: int = 600, agent_id: str | None = None):
    """Renders the official ElevenLabs ConvAI widget via Streamlit components.html."""
    target_agent_id = agent_id or get_elevenlabs_agent_id()

    embed_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <style>
        * {{
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }}
        html, body {{
          width: 100%;
          height: 100%;
          background: transparent;
          overflow: hidden;
          font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
        }}
        .widget-wrapper {{
          width: 100%;
          height: 100%;
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
        }}
      </style>
    </head>
    <body>
      <div class="widget-wrapper">
        <elevenlabs-convai 
          agent-id="{target_agent_id}"
          action-text="Talk to Travel Concierge"
          start-call-text="Start Voice Call"
          end-call-text="End Call"
          listening-text="Listening to your travel plans..."
          speaking-text="TravelPilot speaking..."
        ></elevenlabs-convai>
      </div>

      <script
        src="https://unpkg.com/@elevenlabs/convai-widget-embed"
        async
        type="text/javascript">
      </script>
    </body>
    </html>
    """

    components.html(embed_html, height=height)


def render_voice_agent_card():
    """Renders a modern glassmorphic card showcasing the ElevenLabs Voice Assistant."""
    with st.container(border=True):
        header_col, badge_col = st.columns([4, 1])
        with header_col:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                    <span style="font-size: 1.5rem;">🎙️</span>
                    <div>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #F1F5F9;">
                            TravelPilot AI Voice Concierge
                        </div>
                        <div style="font-size: 0.82rem; color: #94A3B8;">
                            Powered by ElevenLabs Conversational Voice AI • Real-Time Voice Interaction
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with badge_col:
            st.markdown(
                """
                <div style="text-align: right; padding-top: 4px;">
                    <span style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 9999px; padding: 3px 10px; font-size: 0.74rem; font-weight: 700; text-transform: uppercase;">
                        🟢 Live Voice
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption(
            "Speak directly with our AI travel assistant. Ask questions about local bus routes, weather conditions, packing lists, or budget tips."
        )

        prompt_c1, prompt_c2, prompt_c3 = st.columns(3)
        with prompt_c1:
            st.markdown(
                """
                <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px; font-size: 0.8rem; color: #CBD5E1;">
                    🗣️ <i>"Plan a 3-day budget trip to Manali under ₹3,000"</i>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with prompt_c2:
            st.markdown(
                """
                <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px; font-size: 0.8rem; color: #CBD5E1;">
                    🗣️ <i>"What are the HRTC bus timings from Bhuntar to Bijli Mahadev?"</i>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with prompt_c3:
            st.markdown(
                """
                <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px; font-size: 0.8rem; color: #CBD5E1;">
                    🗣️ <i>"Where can I rent tents and camp overnight safely?"</i>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        render_elevenlabs_widget(height=480)


def render_floating_voice_agent(agent_id: str | None = None):
    """Renders the official ElevenLabs ConvAI widget as a sleek floating button attached
    directly to the main window. Takes 0 vertical space in the Streamlit page layout.
    """
    target_agent_id = agent_id or get_elevenlabs_agent_id()

    floating_html = f"""
    <script>
    (function() {{
        try {{
            const doc = window.parent.document;
            if (!doc.getElementById('elevenlabs-convai-widget')) {{
                // 1. Inject ElevenLabs embed script into parent head
                if (!doc.getElementById('elevenlabs-script-loader')) {{
                    const script = doc.createElement('script');
                    script.id = 'elevenlabs-script-loader';
                    script.src = "https://unpkg.com/@elevenlabs/convai-widget-embed";
                    script.async = true;
                    script.type = "text/javascript";
                    doc.head.appendChild(script);
                }}

                // 2. Inject floating custom element into parent body
                const widget = doc.createElement('elevenlabs-convai');
                widget.id = 'elevenlabs-convai-widget';
                widget.setAttribute('agent-id', '{target_agent_id}');
                widget.setAttribute('action-text', 'Talk to AI Concierge');
                widget.setAttribute('start-call-text', 'Start Voice Call');
                widget.setAttribute('end-call-text', 'End Call');
                doc.body.appendChild(widget);
            }}
        }} catch (err) {{
            console.warn("ElevenLabs floating widget injection:", err);
        }}
    }})();
    </script>
    """
    components.html(floating_html, height=0, width=0)


def render_voice_agent_popover(button_label: str = "🎙️ Voice Concierge"):
    """Renders a top navbar popover containing the ElevenLabs Voice Agent."""
    with st.popover(button_label, use_container_width=True):
        st.markdown("### 🎙️ ElevenLabs Voice Concierge")
        st.caption("Real-time two-way voice conversation powered by ElevenLabs ConvAI.")
        render_elevenlabs_widget(height=520)
