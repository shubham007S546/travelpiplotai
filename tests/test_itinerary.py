"""Unit tests for spatio-temporal itinerary scheduling and ordering."""

from optimization.itinerary_optimizer import ItineraryOptimizer
from services.mock_providers import MockTransportProvider, MockStayProvider, MockFoodProvider, MockActivityProvider


def test_itinerary_builder_two_days():
    trans_prov = MockTransportProvider()
    stay_prov = MockStayProvider()
    food_prov = MockFoodProvider()
    act_prov = MockActivityProvider()

    out_opts = trans_prov.search_intercity("Mandi", "Shimla", "2026-10-01", 1)
    ret_opts = trans_prov.search_intercity("Shimla", "Mandi", "2026-10-02", 1)
    stay_opts = stay_prov.search_stays("Shimla", "2026-10-01", "2026-10-02", 1, "budget")
    food_opts = food_prov.search_food("Shimla", "Central", "local", "cheap")
    act_opts = act_prov.search_activities("Shimla", ["heritage"], 3000)

    itinerary = ItineraryOptimizer.build_itinerary(
        duration_days=2,
        source="Mandi",
        destination="Shimla",
        outbound_transport=out_opts[0],
        return_transport=ret_opts[0],
        stay=stay_opts[0],
        food_list=food_opts,
        activities=act_opts
    )

    assert len(itinerary) == 2
    assert itinerary[0].day_number == 1
    assert itinerary[1].day_number == 2
    assert len(itinerary[0].items) >= 4
    assert len(itinerary[1].items) >= 3

    # Check that day 1 starts with transit and day 2 ends with return transit
    assert itinerary[0].items[0].item_type == "travel"
    assert itinerary[1].items[-1].item_type == "travel"
