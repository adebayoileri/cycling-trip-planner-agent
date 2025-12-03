"""Tests for cycling tools."""
import pytest
from src.tools import CyclingTools


class TestCyclingTools:
    """Test suite for CyclingTools."""
    
    def test_get_route_known_route(self):
        """Test getting a known route."""
        result = CyclingTools.get_route("Amsterdam", "Copenhagen", daily_distance_km=100)
        
        assert result["start"] == "Amsterdam"
        assert result["end"] == "Copenhagen"
        assert result["distance_km"] == 680
        assert result["estimated_days"] == 6
        assert len(result["waypoints"]) == 5
        assert "Amsterdam" in result["waypoints"]
        assert "Copenhagen" in result["waypoints"]
    
    def test_get_route_unknown_route(self):
        """Test getting an unknown route (fallback)."""
        result = CyclingTools.get_route("Berlin", "Munich", daily_distance_km=80)
        
        assert result["start"] == "Berlin"
        assert result["end"] == "Munich"
        assert result["distance_km"] > 0
        assert result["estimated_days"] > 0
        assert len(result["waypoints"]) >= 2
    
    def test_get_route_custom_daily_distance(self):
        """Test route calculation with custom daily distance."""
        result = CyclingTools.get_route("Amsterdam", "Copenhagen", daily_distance_km=50)
        
        # 680km at 50km/day should be 13-14 days
        assert result["estimated_days"] >= 13
    
    def test_find_accommodation_known_location(self):
        """Test finding accommodation in a known location."""
        result = CyclingTools.find_accommodation("Bremen", type="any")
        
        assert len(result) >= 2
        assert all("name" in acc for acc in result)
        assert all("type" in acc for acc in result)
        assert all("price_per_night" in acc for acc in result)
    
    def test_find_accommodation_filter_by_type(self):
        """Test filtering accommodation by type."""
        camping = CyclingTools.find_accommodation("Hamburg", type="camping")
        hostels = CyclingTools.find_accommodation("Hamburg", type="hostel")
        
        assert len(camping) >= 1
        assert all(acc["type"] == "camping" for acc in camping)
        
        assert len(hostels) >= 1
        assert all(acc["type"] == "hostel" for acc in hostels)
    
    def test_find_accommodation_unknown_location(self):
        """Test finding accommodation in an unknown location (fallback)."""
        result = CyclingTools.find_accommodation("UnknownCity")
        
        assert len(result) >= 2
        assert result[0]["location"] == "UnknownCity"
    
    def test_get_weather_known_location(self):
        """Test getting weather for a known location."""
        result = CyclingTools.get_weather("Amsterdam", "June")
        
        assert result["location"] == "Amsterdam"
        assert result["month"] == "June"
        assert result["avg_temp_high"] == 20
        assert result["avg_temp_low"] == 12
        assert "cycling_suitability" in result
    
    def test_get_weather_unknown_location(self):
        """Test getting weather for an unknown location (fallback)."""
        result = CyclingTools.get_weather("TestCity", "July")
        
        assert result["location"] == "TestCity"
        assert result["month"] == "July"
        assert result["avg_temp_high"] > 0
        assert result["avg_temp_low"] > 0
        assert result["precipitation_mm"] >= 0
    
    def test_get_weather_suitability_assessment(self):
        """Test that weather suitability is properly assessed."""
        result = CyclingTools.get_weather("Amsterdam", "June")
        
        assert "cycling_suitability" in result
        assert len(result["cycling_suitability"]) > 0
    
    def test_get_elevation_profile_known_segment(self):
        """Test getting elevation for a known route segment."""
        result = CyclingTools.get_elevation_profile("Amsterdam", "Bremen")
        
        assert result["location"] == "Amsterdam to Bremen"
        assert result["total_elevation_gain_m"] == 120
        assert result["difficulty_rating"] == "easy"
        assert "description" in result
    
    def test_get_elevation_profile_unknown_segment(self):
        """Test getting elevation for an unknown segment (fallback)."""
        result = CyclingTools.get_elevation_profile("CityA", "CityB")
        
        assert "CityA" in result["location"]
        assert "CityB" in result["location"]
        assert result["total_elevation_gain_m"] > 0
        assert result["difficulty_rating"] in ["easy", "moderate", "challenging", "difficult"]
    
    def test_get_points_of_interest(self):
        """Test getting points of interest."""
        result = CyclingTools.get_points_of_interest("Hamburg")
        
        assert len(result) >= 1
        assert all("name" in poi for poi in result)
        assert all("type" in poi for poi in result)
        assert all("description" in poi for poi in result)
    
    def test_get_points_of_interest_filter_by_type(self):
        """Test filtering POIs by type."""
        historical = CyclingTools.get_points_of_interest("Bremen", type="historical")
        scenic = CyclingTools.get_points_of_interest("Bremen", type="scenic")
        
        assert len(historical) >= 1
        assert all(poi["type"] == "historical" for poi in historical)
        
        assert len(scenic) >= 1
        assert all(poi["type"] == "scenic" for poi in scenic)
    
    def test_tool_definitions_structure(self):
        """Test that tool definitions have correct structure."""
        tools = CyclingTools.get_tool_definitions()
        
        assert len(tools) == 5
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert "type" in tool["input_schema"]
            assert "properties" in tool["input_schema"]
            assert "required" in tool["input_schema"]
    
    def test_execute_tool_get_route(self):
        """Test executing get_route via execute_tool."""
        result = CyclingTools.execute_tool(
            "get_route",
            {"start": "Amsterdam", "end": "Copenhagen"}
        )
        
        assert result["start"] == "Amsterdam"
        assert result["end"] == "Copenhagen"
    
    def test_execute_tool_invalid_name(self):
        """Test that executing an invalid tool raises an error."""
        with pytest.raises(ValueError, match="Unknown tool"):
            CyclingTools.execute_tool("invalid_tool", {})
    
    def test_accommodation_has_amenities(self):
        """Test that accommodations include amenities."""
        result = CyclingTools.find_accommodation("Hamburg")
        
        for acc in result:
            assert "amenities" in acc
            assert isinstance(acc["amenities"], list)
            assert len(acc["amenities"]) > 0
    
    def test_elevation_difficulty_levels(self):
        """Test that different routes have appropriate difficulty levels."""
        easy = CyclingTools.get_elevation_profile("Amsterdam", "Bremen")
        moderate = CyclingTools.get_elevation_profile("Hamburg", "Lübeck")
        
        assert easy["difficulty_rating"] == "easy"
        assert moderate["difficulty_rating"] == "moderate"
        
        # Easy should have less elevation gain
        assert easy["total_elevation_gain_m"] < moderate["total_elevation_gain_m"]
