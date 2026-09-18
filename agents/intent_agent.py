"""Agent 1 — Intent / Trip Requirement Agent."""

import os
import re
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()
from agents.base_agent import BaseAgent
from models.travel_state import TravelState
from utils.logging import logger


class IntentAgent(BaseAgent):
    """Parses natural-language user travel queries into structured trip parameters."""

    def __init__(self):
        super().__init__(name="Intent Agent")

    def _process(self, state: TravelState) -> Tuple[TravelState, str, List[str], float]:
        query = state.get("user_query", "").strip()
        tool_calls: List[str] = []
        inferred_fields: List[str] = []

        # Attempt LLM extraction if Groq API key is available
        llm_parsed = False
        groq_key = os.getenv("GROQ_API_KEY", "")
        if groq_key and len(groq_key) > 5:
            try:
                tool_calls.append("Groq LLM (openai/gpt-oss-120b) JSON parser")
                parsed_data = self._parse_with_groq(query, groq_key)
                if parsed_data and isinstance(parsed_data, dict):
                    # Filter out null, None, and empty string fields to prevent clobbering existing state
                    clean_data = {}
                    for k, v in parsed_data.items():
                        if v is not None and v != "":
                            if k == "budget":
                                try:
                                    b_flt = float(v)
                                    if b_flt > 0:
                                        clean_data[k] = b_flt
                                except (ValueError, TypeError):
                                    pass
                            elif k in ("duration_days", "travelers"):
                                try:
                                    val_int = int(v)
                                    if val_int > 0:
                                        clean_data[k] = val_int
                                except (ValueError, TypeError):
                                    pass
                            elif k in ("source", "destination"):
                                if isinstance(v, str) and len(v.strip()) > 1:
                                    clean_data[k] = v.strip().title()
                            elif k == "interests" and isinstance(v, list) and v:
                                clean_data[k] = [str(item) for item in v if item]
                            else:
                                clean_data[k] = v

                    if clean_data:
                        state.update(clean_data)
                        llm_parsed = True
            except Exception as e:
                logger.warning(f"Intent LLM parsing failed: {e}. Falling back to rule-based NLP.")

        # Always run rule-based / regex extraction to backfill any missing or unparsed fields
        # 1. Budget & Currency
        if not state.get("budget") or state.get("budget", 0) <= 0:
            budget_match = re.search(r'(?:₹|rs\.?|inr|rupees?)\s*([\d,]+)|([\d,]+)\s*(?:₹|rs\.?|inr|rupees?)', query, re.IGNORECASE)
            if budget_match:
                b_str = (budget_match.group(1) or budget_match.group(2)).replace(",", "")
                state["budget"] = float(b_str)
                state["currency"] = "INR"
            else:
                state["budget"] = 3000.0
                state["currency"] = "INR"
                inferred_fields.append("budget")
        if not state.get("currency"):
            state["currency"] = "INR"

        # 2. Source and Destination
        if not state.get("source") or not state.get("destination"):
            # Check "from X to Y"
            from_to_match = re.search(r'from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s+for|\s+with|\s+in|\s+and|\s+then|\s+we|\.|$)', query, re.IGNORECASE)
            if from_to_match:
                if not state.get("source"):
                    state["source"] = from_to_match.group(1).strip().title()
                if not state.get("destination"):
                    state["destination"] = from_to_match.group(2).strip().title()
            else:
                # Check "place X to Y" or "X to Y"
                x_to_y_match = re.search(r'(?:place\s+|go\s+|travel\s+)?([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s+with|\s+for|\s+and|\s+then|\s+we|\.|$)', query, re.IGNORECASE)
                if x_to_y_match:
                    cand_src = re.sub(r'^(?:i\s+put\s+the\s+place\s+|i\s+want\s+to\s+go\s+|place\s+)', '', x_to_y_match.group(1), flags=re.IGNORECASE).strip()
                    cand_dst = x_to_y_match.group(2).strip()
                    # Filter out short conversational fillers
                    if cand_src and len(cand_src) > 1 and not cand_src.lower() in ("want", "trip", "plan"):
                        if not state.get("source"):
                            state["source"] = cand_src.title()
                    if cand_dst and len(cand_dst) > 1:
                        if not state.get("destination"):
                            state["destination"] = cand_dst.title()
                else:
                    to_match = re.search(r'to\s+([A-Za-z\s]+?)(?:\s+for|\s+with|\s+from|\s+and|\s+then|\s+we|\.|$)', query, re.IGNORECASE)
                    if to_match and not state.get("destination"):
                        state["destination"] = to_match.group(1).strip().title()

        if not state.get("source"):
            state["source"] = "Mandi"
            inferred_fields.append("source")
        if not state.get("destination"):
            state["destination"] = "Shimla"
            inferred_fields.append("destination")

        # 3. Travelers
        if not state.get("travelers") or state.get("travelers", 0) <= 0:
            travelers = 1
            if re.search(r'alone|solo|myself|single', query, re.IGNORECASE):
                travelers = 1
            elif re.search(r'friend|partner|couple|2\s*people|two\s*people|we\b', query, re.IGNORECASE):
                travelers = 2
            else:
                trav_match = re.search(r'(\d+)\s*(?:travelers?|people|persons?|friends?)', query, re.IGNORECASE)
                if trav_match:
                    travelers = int(trav_match.group(1))
                else:
                    inferred_fields.append("travelers")
            state["travelers"] = max(1, travelers)

        # 4. Duration
        if not state.get("duration_days") or state.get("duration_days", 0) <= 0:
            days = 2
            days_match = re.search(r'(\d+)\s*(?:days?|day)', query, re.IGNORECASE)
            if days_match:
                days = int(days_match.group(1))
            elif re.search(r'two\s*days?', query, re.IGNORECASE):
                days = 2
            elif re.search(r'one\s*day|1\s*day', query, re.IGNORECASE):
                days = 1
            else:
                inferred_fields.append("duration_days")
            state["duration_days"] = max(1, days)

        # 5. Preferences
        if not state.get("travel_style"):
            state["travel_style"] = "budget" if re.search(r'cheap|budget|affordable', query, re.IGNORECASE) else "standard"
        if not state.get("transport_preference"):
            state["transport_preference"] = "cheapest practical" if re.search(r'cheap.*transport|bus|shared', query, re.IGNORECASE) else "convenient"
        acc_pref = str(state.get("accommodation_preference", "")).lower()
        if "camp" in acc_pref or "tent" in acc_pref or re.search(r'camp|camping|tent|rent.*tent|night.*camp', query, re.IGNORECASE):
            state["accommodation_preference"] = "camping"
        elif "hostel" in acc_pref or "budget" in acc_pref or re.search(r'safe.*stay|budget.*stay|hostel|homestay', query, re.IGNORECASE):
            state["accommodation_preference"] = "budget"
        elif not state.get("accommodation_preference"):
            state["accommodation_preference"] = "comfortable"
        if not state.get("food_preference"):
            state["food_preference"] = "local" if re.search(r'local.*food|dhaba|thali|street', query, re.IGNORECASE) else "standard"

        if not state.get("interests"):
            interests = []
            if re.search(r'temple|spiritual|mahadev|shiv', query, re.IGNORECASE):
                interests.append("temples")
            if re.search(r'trak|trek|trekking|hike|hiking', query, re.IGNORECASE):
                interests.append("trekking")
            if re.search(r'camp|camping|tent', query, re.IGNORECASE):
                interests.append("camping")
            if re.search(r'nature|scenic|mountain|view', query, re.IGNORECASE):
                interests.append("viewpoints")
            if re.search(r'heritage|history|museum', query, re.IGNORECASE):
                interests.append("heritage")
            if not interests:
                interests = ["viewpoints", "heritage", "local markets"]
            state["interests"] = interests

        state["inferred_fields"] = inferred_fields
        budget_disp = float(state.get("budget") or 3000.0)
        curr_disp = state.get("currency") or "INR"
        trav_disp = int(state.get("travelers") or 1)
        dur_disp = int(state.get("duration_days") or 2)

        summary = (
            f"Extracted: {state.get('source')} → {state.get('destination')} | "
            f"Budget: {curr_disp} {budget_disp:.0f} | "
            f"Travelers: {trav_disp} | Days: {dur_disp} | "
            f"Inferred: {inferred_fields if inferred_fields else 'None'}"
        )
        return state, summary, tool_calls, 0.95

    def _parse_with_groq(self, query: str, api_key: str) -> dict:
        """Invokes Groq model to extract structured JSON parameters."""
        import json
        import re
        from groq import Groq

        client = Groq(api_key=api_key)
        sys_prompt = (
            "Extract travel intent from user query as JSON with keys: "
            "source (string), destination (string), budget (float), currency (string, e.g. INR), travelers (int), duration_days (int), "
            "travel_style (budget/luxury), transport_preference (string), accommodation_preference (string), food_preference (string), interests (list of strings). "
            "Return ONLY a valid JSON object without markdown or code fences."
        )
        res = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.0
        )
        raw_text = res.choices[0].message.content.strip()
        # Clean potential markdown fences
        clean_text = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
        clean_text = re.sub(r"^```\s*", "", clean_text, flags=re.MULTILINE).strip()
        return json.loads(clean_text)
