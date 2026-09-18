"""Ground Reality and Practical Traveler Essentials Service.

Generates ground-truth practical field guidance for everyday travelers
navigating cash/UPI blackouts, network drops, luggage storage,
local taxi touts, and mountain road motion sickness.
"""

from typing import Optional, Dict, Any, List
from models.place import ResolvedPlace
from models.ground_reality import GroundRealityCheck
from models.travel_state import WeatherForecast


class GroundRealityService:
    """Evaluates practical on-the-ground friction points for real-world travelers."""

    @staticmethod
    def generate_ground_reality_kit(
        destination: Optional[ResolvedPlace],
        source: Optional[ResolvedPlace] = None,
        weather: Optional[WeatherForecast] = None
    ) -> GroundRealityCheck:
        dest_name = destination.canonical_name if destination else "Destination"
        dest_lower = dest_name.lower()
        state_lower = (destination.state or "").lower() if destination else ""
        is_rural = getattr(destination, "is_rural", False) if destination else False
        is_trek = getattr(destination, "is_trek_destination", False) if destination else False
        place_type = getattr(destination, "place_type", "") if destination else ""

        # 1. Identify Regional Category
        is_himalayan = any(s in state_lower for s in ("himachal", "uttarakhand", "jammu", "kashmir", "ladakh", "sikkim"))
        is_pilgrimage = any(k in dest_lower for k in ("haridwar", "rishikesh", "varanasi", "rewalsar", "bijli", "temple", "shrine", "ghat", "kanda"))
        is_metro = any(k in dest_lower for k in ("delhi", "bangalore", "bengaluru", "mumbai", "pune", "chennai", "kolkata", "hyderabad"))
        is_remote_mountain = is_trek or is_rural or any(k in dest_lower for k in ("prashar", "chitkul", "yulla", "sangla", "tosh", "kasol", "jibhi", "baggi", "tapri", "karcham"))

        # -------------------------------------------------------------
        # 2. Financial / Digital Payment Reality
        # -------------------------------------------------------------
        if is_remote_mountain:
            digital_status = "CASH_CRITICAL"
            recommended_cash = 3000.0
            cash_guidance = (
                "⚠️ DIGITAL PAYMENT BLACKOUT ZONE: Do NOT rely on Google Pay, PhonePe, or Paytm here. "
                "Cell tower power cuts and mountain gorges cause frequent transaction timeouts. "
                "Local dhabas, tea stalls, and shared jeeps operate purely on cash. "
                "Carry at least ₹3,000 in physical cash per traveler."
            )
            # Identify last reliable ATM hub
            if any(k in dest_lower for k in ("prashar", "baggi", "rewalsar")):
                last_atm = "Mandi Town or Nerchowk (last working ATMs before ascending to ridge)"
            elif any(k in dest_lower for k in ("chitkul", "sangla", "yulla", "tapri")):
                last_atm = "Reckong Peo / Rampur Bushahr (ATMs beyond Tapri are frequently out of cash)"
            elif any(k in dest_lower for k in ("bijli mahadev", "chansari")):
                last_atm = "Bhuntar or Kullu Town Bus Stand"
            else:
                last_atm = "Nearest Sub-Divisional Headquarter or Highway Junction"
        elif is_pilgrimage:
            digital_status = "PARTIAL_UPI"
            recommended_cash = 1500.0
            cash_guidance = (
                "UPI is accepted at established hotels and shops, but temple shoe-keeping stalls, "
                "Ganga boatmen, floral offerings, and local cycle/e-rickshaws demand physical cash. "
                "Keep ₹1,500 per person specifically in small notes (₹10, ₹20, ₹50, ₹100)."
            )
            last_atm = "City Center / Railway Station Entrance"
        elif is_metro:
            digital_status = "DIGITAL_FRIENDLY"
            recommended_cash = 500.0
            cash_guidance = (
                "UPI, credit cards, and contactless transit cards work seamlessly across 98% of outlets. "
                "Keep ₹500 cash for auto meters or street vendors."
            )
            last_atm = "Available at virtually all metro stations and bank kiosks"
        else:
            digital_status = "PARTIAL_UPI"
            recommended_cash = 1500.0
            cash_guidance = (
                "UPI works at main roadside dhabas, but network dropouts can occur. "
                "Keep ₹1,500 reserve cash for toll booths and local auto transit."
            )
            last_atm = "Nearest Bus Stand or Tehsil Center"

        # -------------------------------------------------------------
        # 3. Telecom & SIM Signal Reliability
        # -------------------------------------------------------------
        if is_remote_mountain:
            telecom = {
                "Jio": "4G Available in pockets; drops inside gorges",
                "BSNL": "Strongest lifeline coverage across tribal HP valleys",
                "Airtel": "Spotty / Frequently 'No Service' at remote trailheads",
                "Vi (Vodafone Idea)": "Generally No Signal in valley interiors"
            }
            offline_warning = (
                "📱 SIGNAL BLACKOUT WARNING: Download offline Google Maps, take screenshots of hotel booking IDs "
                "and host phone numbers, and keep a printed or offline copy of your TravelPilot PDF pass before departing the highway hub."
            )
        elif is_himalayan:
            telecom = {
                "Jio": "Consistent 4G / 5G along main highway corridors",
                "Airtel": "Reliable in town centers; weak on interior detour roads",
                "BSNL": "Dependable fallback throughout hill districts",
                "Vi": "Moderate in municipal areas; weak on highways"
            }
            offline_warning = "Download offline maps for mountain sections where highway cellular handoffs cause brief GPS dropouts."
        else:
            telecom = {
                "Jio": "High-Speed 4G / 5G Nationwide",
                "Airtel": "High-Speed 4G / 5G Nationwide",
                "Vi": "4G Available in urban and highway zones",
                "BSNL": "Standard 3G/4G coverage"
            }
            offline_warning = "Cellular signal is strong throughout. Keep phone charged for digital payments and transit QR scans."

        # -------------------------------------------------------------
        # 4. Luggage & Cloakroom Management
        # -------------------------------------------------------------
        if is_trek:
            cloakroom_info = (
                "🎒 LUGGAGE ADVISORY (TREK DESTINATION): Do NOT attempt to carry hard trolley bags to the summit trail. "
                "Leave heavy luggage at your base homestay/hotel in the roadhead hub (or at a trusted local tea shop locker) "
                "and hike with a lightweight 15-20L daypack containing water, snacks, warm layer, and essentials."
            )
        elif is_pilgrimage or is_metro:
            cloakroom_info = (
                "🧳 CLOAKROOM FACILITY: If checking out early before an evening train/bus, use the official "
                "Railway Station Cloakroom (IRCTC rules require luggage to be securely locked with a padlock; ₹20–₹40/day) "
                "or the central ISBT bus terminal locker room."
            )
        else:
            cloakroom_info = (
                "Most hotels and registered homestays provide complimentary luggage holding after 11:00 AM checkout. "
                "Confirm holding pickup time with the front desk before heading out."
            )

        # -------------------------------------------------------------
        # 5. Anti-Scam & Local Transit Defense
        # -------------------------------------------------------------
        if is_remote_mountain:
            anti_scam = (
                "🚕 TAXI UNION DEFENSE: Ignore touts who approach you inside the bus stand claiming 'no more buses are going today'. "
                "Walk to the designated Himachal Taxi Operators Union counter or ask the HRTC enquiry booth for the next ordinary stage carriage "
                "or local shared jeep (Maxi-Cab) departing from the stand."
            )
            statutory_tip = "Shared maxi-cabs typically cost ₹30–₹80 per seat for valley runs, compared to ₹800–₹1,500 for an unmetered private cab."
        elif is_pilgrimage:
            anti_scam = (
                "🛕 PILGRIM SAFETY: Beware of unauthorized 'guides' or fake priest touts at river ghats and temple queues demanding "
                "forced 'donation receipts' or charging for free darshan lines. Always purchase official puja receipts and prasad "
                "only from the verified temple trust counters."
            )
            statutory_tip = "Use prepaid auto-rickshaw booths outside railway stations or insist on the government meter rate."
        else:
            anti_scam = (
                "🚗 METRO & TRANSIT DEFENSE: Avoid unmetered street cabs. Use app-based cabs (Uber/Ola) at designated pickup bays "
                "or government prepaid taxi/auto booths located at railway station exits."
            )
            statutory_tip = "Verify driver name and vehicle registration number against your booking confirmation before boarding."

        # -------------------------------------------------------------
        # 6. Health, Motion Sickness & Terrain Readiness
        # -------------------------------------------------------------
        ams_risk = False
        if any(k in dest_lower for k in ("prashar", "yulla", "chitkul")):
            ams_risk = True
            health_advice = (
                "⛰️ ALTITUDE & MOTION SICKNESS ALERT: Destination elevation exceeds 2,500 meters (thin air & rapid temperature drops). "
                "Take winding ghat road precautions: avoid heavy oily meals before traveling; take preventive motion sickness medication "
                "(e.g. Avomine / Ginger candy) 30 mins before the ascent. Drink 3 liters of water; avoid alcohol to prevent Acute Mountain Sickness (AMS)."
            )
        elif is_himalayan:
            health_advice = (
                "🤢 GHAT ROAD MOTION SICKNESS: Mountain highway involves hundreds of continuous hairpin bends. "
                "Sit in the front or middle rows of buses (avoid the bouncy rear axle). Keep a window cracked for fresh mountain air. "
                "Carry motion sickness tablets and sick bags in your daypack."
            )
        else:
            health_advice = (
                "💧 HYDRATION & HYGIENE: Carry an insulated reusable water bottle. Consume only RO filtered or sealed packaged drinking water. "
                "Keep basic first-aid: Paracetamol, ORS electrolytes, and antacid tablets."
            )

        # -------------------------------------------------------------
        # 7. Climate, Clothing, Power & Women/Family Tips
        # -------------------------------------------------------------
        if is_himalayan:
            clothing_power = (
                "🧥 RAPID TEMPERATURE SWINGS: Hill weather can shift from sunny (22°C) to chilling (5°C) in under 30 minutes. "
                "Pack layered clothing (thermal inner + fleece + windproof jacket). "
                "🔋 COLD BATTERY DRAIN: Lithium-ion phone batteries discharge up to 3x faster in cold air. "
                "Carry a 10,000+ mAh power bank and keep your phone in an inside pocket close to body warmth."
            )
        else:
            clothing_power = (
                "Wear breathable cotton clothing, comfortable walking shoes, and carry a compact power bank (phone navigation uses extra battery)."
            )

        women_family = (
            "🚻 RESTROOM & FAMILY AMENITIES: Along highway corridors, prefer designated HP Tourism / State Tourism wayside complexes "
            "or major fuel company stations (IndianOil Swagat, BPCL Ghar) which maintain clean, accessible restrooms for women and families. "
            "Emergency Police & Women Helpline: 112 (or 1091)."
        )

        # -------------------------------------------------------------
        # 8. Practical Packing Checklist
        # -------------------------------------------------------------
        checklist = [
            f"Physical cash: Minimum ₹{recommended_cash:.0f} per traveler (small notes: ₹10, ₹20, ₹50, ₹100)",
            "Government Photo ID (Aadhaar Card / Voter ID / Passport) for hotel check-ins and forest check-posts",
            "Offline downloads: Google Maps area map, TravelPass PDF, screenshots of host contact & address",
            "High-capacity power bank (10,000 to 20,000 mAh) + charging cable",
            "Motion sickness medication (Avomine/Stugeron) + ORS hydration sachets + basic first aid"
        ]
        if is_himalayan:
            checklist.extend([
                "Thermal inner wear + windproof fleece jacket + woollen cap/gloves",
                "Sturdy shoes with good rubber traction (avoid flat smooth-soled sneakers on wet trails)",
                "UV-protection sunglasses & SPF sunscreen (high altitude UV radiation is 30% stronger)"
            ])
        if is_trek:
            checklist.extend([
                "15–20L lightweight daypack for summit hike (leave heavy trolley bags at base)",
                "Refillable 1-liter water bottle + high-energy trail snacks (dry fruits, glucose biscuits)",
                "Compact flashlight / headlamp (mountain trails get pitch black immediately after sunset)"
            ])

        return GroundRealityCheck(
            destination=dest_name,
            region_type="hills" if is_himalayan else ("pilgrimage" if is_pilgrimage else ("metro" if is_metro else "rural")),
            digital_payment_status=digital_status,
            cash_guidance=cash_guidance,
            recommended_cash_inr=recommended_cash,
            last_atm_hub=last_atm,
            telecom_networks=telecom,
            offline_readiness_warning=offline_warning,
            luggage_cloakroom_info=cloakroom_info,
            anti_scam_transit_advice=anti_scam,
            statutory_fare_tip=statutory_tip,
            health_motion_sickness_advice=health_advice,
            altitude_ams_risk=ams_risk,
            clothing_and_power_advice=clothing_power,
            women_and_family_tips=women_family,
            packing_checklist=checklist
        )
