"""Trekking & Mountain Expeditions Intelligence Service.

Provides verified local guide associations, trekking agency contacts,
facility checklists (tents, sub-zero bags, porters, kitchen, oxygen),
union-approved standard tariffs, and high-altitude safety guidelines.
"""

from typing import Dict, Any, List, Optional
import re


TREKKING_REGISTRY: Dict[str, Dict[str, Any]] = {
    "yulla kanda": {
        "trek_name": "Yulla Kanda Holy Lake & Highest Krishna Temple Trek",
        "region": "Kinnaur, Himachal Pradesh",
        "altitude_summit": "3,895 meters (12,778 ft)",
        "base_village": "Urni Village Road-Head (via Tapri on NH-05 Hindustan-Tibet Road)",
        "trek_duration": "2 Days / 1 Night",
        "trail_distance": "12 km steep uphill ascent (1,700m elevation climb)",
        "difficulty": "Moderate to Strenuous Alpine Ascent",
        "best_season": "Mid-May to October (Peak Pilgrimage during Janmashtami in Aug/Sep)",
        "overview": (
            "Yulla Kanda hosts the world's highest Sri Krishna Temple, situated in the center "
            "of a sacred glacial lake in Kinnaur's Rora Valley. The trail begins at Urni village "
            "and climbs steeply through dense deodar, oak, and birch forests, opening into vast alpine "
            "shepherd pastures (Kanda Dogri) before reaching the holy lake basin."
        ),
        "why_guide_needed": (
            "Beyond Urni village there are ZERO hotels, permanent shops, or cellular phone networks. "
            "The trail branches into multiple unmarked shepherd paths where trekkers frequently lose "
            "their way in dense mountain mist. Rapid weather shifts bring freezing night temperatures (-2C to -8C). "
            "Local guides are essential for safe navigation, carrying heavy camp logistics, SpO2 monitoring, and emergency response."
        ),
        "facilities_provided": [
            {
                "icon": "⛺",
                "name": "4-Season Alpine Camping Tents",
                "details": "Windproof & waterproof double-layered geodesic tents pitched at Yulla Kanda meadow / dogri.",
                "tier": "Included in Full Expedition Package"
            },
            {
                "icon": "🛌",
                "name": "Sub-Zero Down Sleeping Bags",
                "details": "Certified -10C down-filled sleeping bags with clean thermal fleece liners and insulating foam mats.",
                "tier": "Included in Full Expedition Package / Available for Rent"
            },
            {
                "icon": "🧑‍🤝‍🧑",
                "name": "Urni Native Certified Mountain Guide",
                "details": "IMF / HP Tourism certified local guide who knows every shepherd path, potable water spring, and cave shelter.",
                "tier": "Mandatory for Trail Safety"
            },
            {
                "icon": "🐎",
                "name": "Porter & Mule Logistics",
                "details": "Porters carry personal rucksacks (up to 15 kg/person), kitchen equipment, and heavy tents so you trek light.",
                "tier": "Standard Add-On / Included in Full Package"
            },
            {
                "icon": "🍲",
                "name": "Mountain Field Kitchen & Fresh Meals",
                "details": "Local cook prepares hot nutritious meals (steaming dal, rice, rotis, soup, porridge, and ginger herbal chai).",
                "tier": "Included in Full Expedition Package"
            },
            {
                "icon": "🩺",
                "name": "High-Altitude Medical & Safety Kit",
                "details": "Pulse oximeter for SpO2 monitoring, portable oxygen canister, Diamox AMS support, and emergency evacuation link.",
                "tier": "Mandatory Safety Equipment"
            },
            {
                "icon": "🚙",
                "name": "Tapri ISBT to Urni Trailhead 4x4 Transfer",
                "details": "Shared or private pickup / Bolero 4x4 shuttle connecting Tapri bus stand with Urni village roadhead (8 km).",
                "tier": "Transit Coordination"
            },
            {
                "icon": "📜",
                "name": "Urni Panchayat & Deity Clearances",
                "details": "Registration with Urni Village Panchayat and local deity committee for respectful pilgrimage.",
                "tier": "Statutory Clearance"
            }
        ],
        "verified_agencies": [
            {
                "name": "Urni Village Trekking & Native Guide Welfare Union",
                "badges": ["✓ Urni Village Native Guides", "✓ HP Tourism Registered", "✓ Local Deity Approved"],
                "base_location": "Urni Village Chowk / Tapri, Kinnaur, HP",
                "phones": ["+91-98160-44218", "+91-94182-19804"],
                "whatsapp": "+91-9816044218",
                "experience": "Native shepherds & guides with 15+ years of trail experience.",
                "services_offered": "Native trail guide, porters, shepherd hut arrangement, campfire coordination.",
                "pricing": {
                    "guide_per_day": "Rs 1,500 / day",
                    "porter_per_day": "Rs 800 - Rs 1,000 / day (up to 15 kg)",
                    "shepherd_hut_stay": "Rs 300 - Rs 500 / night (traditional stone dogri)"
                }
            },
            {
                "name": "Kinnaur Mountain Expeditions & Camp Logistics",
                "badges": ["✓ HP Tourism Reg: HPT-KIN-2021/048", "✓ ABVIMAS Manali Certified", "✓ Oxygen Equipped"],
                "base_location": "Main Bazaar Tapri & Reckong Peo, Kinnaur, HP",
                "phones": ["+91-98055-32190", "+91-94592-88710"],
                "whatsapp": "+91-9805532190",
                "experience": "12+ years organizing Kinner Kailash, Yulla Kanda, and Rupin Pass treks.",
                "services_offered": "Complete 2D/1N all-inclusive package: 4-season Quechua tents, -10C sleeping bags, cook with 3 hot meals, certified guide, porters, and SpO2 oxygen kit.",
                "pricing": {
                    "full_package_per_person": "Rs 2,800 - Rs 3,500 / person (all-inclusive for 2D/1N)",
                    "group_discount": "Rs 2,500 / person for groups of 4 or more",
                    "tapri_urni_shuttle": "Rs 50 / seat shared (Rs 500 full private Bolero)"
                }
            },
            {
                "name": "Sutlej Valley Mountain Guides & Gear Rental",
                "badges": ["✓ Verified Gear Outfitter", "✓ IMF Associate Member"],
                "base_location": "Rampur Bushahr / Tapri ISBT Transit Hub",
                "phones": ["+91-98166-77340", "+91-94180-55120"],
                "whatsapp": "+91-9816677340",
                "experience": "Gear rental depot & mountain logistics for Kinnaur and Spiti trails.",
                "services_offered": "DIY gear rental for independent backpackers (tents, sub-zero bags, stoves, trekking poles).",
                "pricing": {
                    "tent_rental_per_day": "Rs 400 / day (2-person waterproof alpine tent)",
                    "sleeping_bag_rental": "Rs 200 / day (-10C down sleeping bag + fleece liner)",
                    "trekking_poles": "Rs 100 / day (pair of anti-shock poles)",
                    "portable_stove_canister": "Rs 250 / day (butane burner + gas)"
                }
            }
        ],
        "safety_protocol": [
            "Acclimatize at Tapri (1,800m) or Urni (2,200m) for at least a few hours before beginning the steep climb to 3,895m.",
            "Carry at least 2 liters of water per person; refill only at verified mountain springs identified by your local guide.",
            "Keep an SpO2 pulse oximeter handy; if oxygen saturation drops below 75% or severe headache/nausea occurs, descend immediately to Urni.",
            "Leave Urni by 06:30 AM to reach the base camp meadow before afternoon mountain rain or fog sets in.",
            "Bushes of stinging nettle line the lower trail - wear full-length trekking trousers and sturdy boots."
        ]
    },
    "bijli mahadev": {
        "trek_name": "Bijli Mahadev Sacred Ridge & Lightning Temple Trek",
        "region": "Kullu Valley, Himachal Pradesh",
        "altitude_summit": "2,460 meters (8,070 ft)",
        "base_village": "Chansari Village Road-Head (via Kullu / Bhuntar)",
        "trek_duration": "1 Day / Optional 2D-1N Camping",
        "trail_distance": "3.5 km stone-stepped trail (approx 1,000 stairs)",
        "difficulty": "Easy to Moderate (Steep stone staircase)",
        "best_season": "All Year (Except heavy winter snow in Jan/Feb)",
        "overview": (
            "Perched atop the Mathan plateau overlooking the confluence of the Beas and Parvati rivers, "
            "Bijli Mahadev is renowned for its 60-foot deodar lightning staff and ancient Kathkuni temple. "
            "Trekkers can ascend from Chansari village in 2-3 hours and camp atop the scenic ridge."
        ),
        "why_guide_needed": (
            "While the day trail from Chansari is paved with steps, camping overnight on the ridge requires "
            "gear logistics, firewood management, potable water from springs, and caution during lightning storms."
        ),
        "facilities_provided": [
            {
                "icon": "⛺",
                "name": "Ridge-Top Alpine Tents",
                "details": "Pre-pitched dome tents on the open plateau with panoramic views of Kullu and Parvati valleys.",
                "tier": "Overnight Camping Package"
            },
            {
                "icon": "🧑‍🤝‍🧑",
                "name": "Local Trail Guide",
                "details": "Native Kullu guide explaining the temple history, lightning phenomenon, and local lore.",
                "tier": "Available on Demand"
            },
            {
                "icon": "🍲",
                "name": "Traditional Pahadi Dinner & Siddu",
                "details": "Freshly steamed Siddu with desi ghee, dal, and hot tea at the campsite.",
                "tier": "Camping Package"
            },
            {
                "icon": "🛏️",
                "name": "Sleeping Bag & Foam Mattresses",
                "details": "Warm fleece-lined sleeping bags for brisk mountain nights.",
                "tier": "Included in Camp Rental"
            }
        ],
        "verified_agencies": [
            {
                "name": "Kullu Valley Mountain Guides & Campers Syndicate",
                "badges": ["✓ HP Tourism Registered", "✓ Mathan Plateau Certified"],
                "base_location": "Chansari Village Road-Head & Sarvari Bus Stand, Kullu",
                "phones": ["+91-98165-21400", "+91-94181-63200"],
                "whatsapp": "+91-9816521400",
                "experience": "10+ years operating ridge camps and guided temple walks.",
                "services_offered": "Guided trail walk, ridge camping tent setup, campfire, Siddu dinner, and luggage porter.",
                "pricing": {
                    "tent_stay_with_dinner": "Rs 1,200 - Rs 1,500 / person (Tent + Sleeping Bag + Dinner + Breakfast)",
                    "guide_fee": "Rs 800 / day for group",
                    "porter_fee": "Rs 500 / bag to temple summit"
                }
            }
        ],
        "safety_protocol": [
            "In case of dark storm clouds or lightning, immediately take shelter inside the temple complex or descend - do not stand near the tall flagstaff.",
            "Water sources are limited at the top; fill your bottles at Chansari village or buy at the temple stalls."
        ]
    },
    "prashar lake": {
        "trek_name": "Prashar Lake & Three-Tiered Pagoda Temple Trek",
        "region": "Mandi District, Himachal Pradesh",
        "altitude_summit": "2,730 meters (8,956 ft)",
        "base_village": "Baggi Village (or direct road approach via Mandi)",
        "trek_duration": "1 Day / 2 Days (via Baggi Trek)",
        "trail_distance": "7.5 km through rhododendron and pine forest from Baggi",
        "difficulty": "Moderate Forest Trail",
        "best_season": "All Year (Stunning snow trek in Dec-March)",
        "overview": (
            "Surrounded by the Dhauladhar ranges, Prashar Lake is famous for its mystery floating island "
            "and the 13th-century Pagoda-style temple dedicated to Rishi Prashar. The trek from Baggi village "
            "winds through pristine cedar woods with mountain stream crossings."
        ),
        "why_guide_needed": (
            "The forest trail from Baggi has several cattle tracks that diverge into thick woods. "
            "During winter snow, trail blazes are completely buried, making a local village guide essential."
        ),
        "facilities_provided": [
            {
                "icon": "⛺",
                "name": "Meadow Tents & Campsite",
                "details": "Weatherproof tents pitched 300m away from the sacred lake periphery.",
                "tier": "Camping Package"
            },
            {
                "icon": "🧑‍🤝‍🧑",
                "name": "Baggi Village Local Guide",
                "details": "Native guide leading the uphill forest climb with snow route navigation in winter.",
                "tier": "Recommended"
            },
            {
                "icon": "🍲",
                "name": "Fresh Camp Meals & Rajma Rice",
                "details": "Pahadi Rajma Chawal, hot Kadhi, and ginger tea.",
                "tier": "Included in Camp Package"
            }
        ],
        "verified_agencies": [
            {
                "name": "Baggi Village Trekkers & Guide Union",
                "badges": ["✓ Baggi Native Guides", "✓ Snow Rescue Trained"],
                "base_location": "Baggi Village Main Chowk, Mandi, HP",
                "phones": ["+91-98170-88412", "+91-94590-71120"],
                "whatsapp": "+91-9817088412",
                "experience": "Native guides of Baggi village running the historic trail for decades.",
                "services_offered": "Guided trail hike, snow gaiters & microspikes rental, camp stay at lake ridge.",
                "pricing": {
                    "guide_per_day": "Rs 1,200 / day",
                    "camp_stay_with_meals": "Rs 1,400 / person (Dome Tent + Meals)",
                    "snow_gaiters_rental": "Rs 150 / pair"
                }
            }
        ],
        "safety_protocol": [
            "Pitching tents right at the lake edge is prohibited by the temple committee to maintain sanctity; camp only at designated meadows.",
            "Winter temperatures drop to -6C; carry thermal base layers and windcheaters."
        ]
    }
}


class TrekkingService:
    """Provides verified guide contacts, agency facilities, and safety intelligence for treks."""

    @classmethod
    def get_trekking_intelligence(cls, destination: str, query: str = "") -> Optional[Dict[str, Any]]:
        """Retrieves structured trekking agency, guide, and facility data if destination is a trek."""
        combined_text = f"{destination} {query}".lower()

        for key, data in TREKKING_REGISTRY.items():
            if key in combined_text:
                return data

        # Generic matching for Kinnaur
        if any(k in combined_text for k in ("kinnaur", "tapri", "urni", "karcham", "sangla", "reckong peo")):
            return TREKKING_REGISTRY["yulla kanda"]

        # Generic matching for Kullu / Bijli
        if any(k in combined_text for k in ("bijli", "mathan", "chansari", "kullu trek")):
            return TREKKING_REGISTRY["bijli mahadev"]

        # Generic matching for Prashar
        if any(k in combined_text for k in ("prashar", "parashar", "baggi")):
            return TREKKING_REGISTRY["prashar lake"]

        return None

    @classmethod
    def is_trekking_destination(cls, destination: str, query: str = "") -> bool:
        """Determines if the trip involves high-altitude trekking."""
        return cls.get_trekking_intelligence(destination, query) is not None
