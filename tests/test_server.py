"""Tests for Stockholm Traffic MCP server."""

import pytest
import responses
from datetime import datetime
import pytz
from unittest.mock import patch

from server import (
    stop_lookup,
    plan_journey,
    _convert_utc_to_stockholm,
    _get_best_time,
    _simplify_journey_response,
    BASE_URL,
)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_convert_utc_to_stockholm(self):
        """Test UTC to Stockholm time conversion."""
        # Test normal conversion
        utc_time = "2025-07-05T11:18:00Z"
        result = _convert_utc_to_stockholm(utc_time)
        assert result == "13:18"  # UTC+2 in summer

        # Test empty string
        assert _convert_utc_to_stockholm("") == ""

        # Test invalid format
        assert _convert_utc_to_stockholm("invalid") == "invalid"

    def test_get_best_time(self):
        """Test getting best available time."""
        # Test with estimated time preferred
        leg_data = {
            "departureTimeEstimated": "2025-07-05T11:18:00Z",
            "departureTimePlanned": "2025-07-05T11:15:00Z",
        }
        result = _get_best_time(leg_data, "departure")
        assert result == "13:18"  # Should prefer estimated

        # Test with only planned time
        leg_data = {"departureTimePlanned": "2025-07-05T11:15:00Z"}
        result = _get_best_time(leg_data, "departure")
        assert result == "13:15"

        # Test with no time data
        leg_data = {}
        result = _get_best_time(leg_data, "departure")
        assert result == ""

    def test_simplify_journey_response(self):
        """Test journey response simplification."""
        mock_response = {
            "journeys": [
                {
                    "tripDuration": 1800,  # 30 minutes
                    "interchanges": 1,
                    "legs": [
                        {
                            "origin": {
                                "name": "T-Centralen",
                                "departureTimeEstimated": "2025-07-05T11:18:00Z",
                            },
                            "destination": {
                                "name": "Odenplan",
                                "arrivalTimeEstimated": "2025-07-05T11:25:00Z",
                            },
                            "product": {
                                "name": "Metro",
                                "line": "19",
                                "direction": "Handen",
                            },
                            "duration": 420,  # 7 minutes
                        }
                    ],
                }
            ],
            "systemMessages": [],
        }

        result = _simplify_journey_response(mock_response)

        assert len(result["journeys"]) == 1
        journey = result["journeys"][0]
        assert journey["duration_minutes"] == 30
        assert journey["interchanges"] == 1
        assert len(journey["legs"]) == 1

        leg = journey["legs"][0]
        assert leg["origin"] == "T-Centralen"
        assert leg["destination"] == "Odenplan"
        assert leg["transport_type"] == "Metro"
        assert leg["line"] == "19"
        assert leg["direction"] == "Handen"
        assert leg["duration_minutes"] == 7


class TestStopLookup:
    """Test stop lookup functionality."""

    @responses.activate
    def test_stop_lookup_success(self):
        """Test successful stop lookup."""
        mock_response = {
            "locations": [
                {
                    "id": "9001",
                    "name": "T-Centralen",
                    "coord": [18.0578, 59.3317],
                    "matchQuality": 1000,
                    "isBest": True,
                },
                {
                    "id": "9002",
                    "name": "Centralen",
                    "coord": [18.0578, 59.3317],
                    "matchQuality": 800,
                    "isBest": False,
                },
            ]
        }

        responses.add(
            responses.GET, f"{BASE_URL}/stop-finder", json=mock_response, status=200
        )

        result = stop_lookup("T-Centralen")

        assert len(result) == 2
        assert result[0]["id"] == "9001"
        assert result[0]["name"] == "T-Centralen"
        assert result[0]["is_best_match"] is True
        assert result[1]["is_best_match"] is False

    @responses.activate
    def test_stop_lookup_error(self):
        """Test stop lookup with API error."""
        responses.add(responses.GET, f"{BASE_URL}/stop-finder", status=500)

        result = stop_lookup("T-Centralen")

        assert len(result) == 1
        assert "error" in result[0]

    @responses.activate
    def test_stop_lookup_empty_response(self):
        """Test stop lookup with empty response."""
        responses.add(
            responses.GET, f"{BASE_URL}/stop-finder", json={"locations": []}, status=200
        )

        result = stop_lookup("NonExistentStop")

        assert result == []


class TestPlanJourney:
    """Test journey planning functionality."""

    @responses.activate
    def test_plan_journey_success(self):
        """Test successful journey planning."""
        mock_response = {
            "journeys": [
                {
                    "tripDuration": 1800,
                    "interchanges": 1,
                    "legs": [
                        {
                            "origin": {
                                "name": "T-Centralen",
                                "departureTimeEstimated": "2025-07-05T11:18:00Z",
                            },
                            "destination": {
                                "name": "Odenplan",
                                "arrivalTimeEstimated": "2025-07-05T11:25:00Z",
                            },
                            "product": {
                                "name": "Metro",
                                "line": "19",
                                "direction": "Handen",
                            },
                            "duration": 420,
                        }
                    ],
                }
            ],
            "systemMessages": [],
        }

        responses.add(
            responses.GET, f"{BASE_URL}/trips", json=mock_response, status=200
        )

        result = plan_journey("9001", "9002")

        assert "journeys" in result
        assert len(result["journeys"]) == 1
        journey = result["journeys"][0]
        assert journey["duration_minutes"] == 30
        assert journey["interchanges"] == 1

    @responses.activate
    def test_plan_journey_with_options(self):
        """Test journey planning with various options."""
        responses.add(
            responses.GET,
            f"{BASE_URL}/trips",
            json={"journeys": [], "systemMessages": []},
            status=200,
        )

        result = plan_journey(
            "9001",
            "9002",
            trips=5,
            exclude_walking=False,
            exclude_transport_types=["bus", "tram"],
            departure_time="14:30",
            max_walking_distance=1000,
        )

        # Check that the request was made with correct parameters
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "calc_number_of_trips=5" in request.url
        assert "maxWalkingDistanceOrigin=1000" in request.url
        assert "time=14%3A30" in request.url

    @responses.activate
    def test_plan_journey_error(self):
        """Test journey planning with API error."""
        responses.add(responses.GET, f"{BASE_URL}/trips", status=500)

        result = plan_journey("9001", "9002")

        assert "error" in result

    def test_plan_journey_invalid_time(self):
        """Test journey planning with invalid departure time."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{BASE_URL}/trips",
                json={"journeys": [], "systemMessages": []},
                status=200,
            )

            # Should not raise an exception with invalid time format
            result = plan_journey("9001", "9002", departure_time="invalid")
            assert "journeys" in result


class TestTransportTypeExclusion:
    """Test transport type exclusion logic."""

    @responses.activate
    def test_exclude_transport_types(self):
        """Test excluding specific transport types."""
        responses.add(
            responses.GET,
            f"{BASE_URL}/trips",
            json={"journeys": [], "systemMessages": []},
            status=200,
        )

        # Test excluding bus and metro
        plan_journey("9001", "9002", exclude_transport_types=["bus", "metro"])

        # Check that excludedMeans parameter was set correctly
        request = responses.calls[0].request
        # Bus (1) + Metro (2) + Walking (32) = 35
        assert "excludedMeans=35" in request.url

    @responses.activate
    def test_exclude_walking_only(self):
        """Test excluding only walking."""
        responses.add(
            responses.GET,
            f"{BASE_URL}/trips",
            json={"journeys": [], "systemMessages": []},
            status=200,
        )

        plan_journey("9001", "9002", exclude_walking=True)

        request = responses.calls[0].request
        # Only walking (32)
        assert "excludedMeans=32" in request.url

    @responses.activate
    def test_no_exclusions(self):
        """Test with no transport type exclusions."""
        responses.add(
            responses.GET,
            f"{BASE_URL}/trips",
            json={"journeys": [], "systemMessages": []},
            status=200,
        )

        plan_journey("9001", "9002", exclude_walking=False)

        request = responses.calls[0].request
        # No excludedMeans parameter should be present
        assert "excludedMeans" not in request.url


@pytest.mark.parametrize(
    "time_str,expected",
    [
        ("2025-07-05T11:18:00Z", "13:18"),
        ("2025-12-15T11:18:00Z", "12:18"),  # Winter time (UTC+1)
        ("", ""),
        ("invalid", "invalid"),
    ],
)
def test_timezone_conversion_parametrized(time_str, expected):
    """Test timezone conversion with various inputs."""
    result = _convert_utc_to_stockholm(time_str)
    assert result == expected
