"""Tool implementations for the cycling trip planner."""
from typing import List, Dict, Any
from src.models import (
    RouteInfo, Accommodation, WeatherInfo, 
    ElevationProfile, PointOfInterest
)


class CyclingTools:
    """Collection of tools for cycling trip planning."""
    
    # Mock data for various European cycling routes
    ROUTE_DATA = {
        ("amsterdam", "copenhagen"): {
            "distance_km": 680,
            "waypoints": ["Amsterdam", "Bremen", "Hamburg", "Lübeck", "Copenhagen"],
            "description": "Classic North Sea route through Netherlands and Germany"
        },
        ("amsterdam", "bruges"): {
            "distance_km": 230,
            "waypoints": ["Amsterdam", "Rotterdam", "Antwerp", "Bruges"],
            "description": "Flat coastal route through Netherlands and Belgium"
        },
        ("paris", "amsterdam"): {
            "distance_km": 520,
            "waypoints": ["Paris", "Amiens", "Lille", "Brussels", "Antwerp", "Amsterdam"],
            "description": "Route through northern France, Belgium, and Netherlands"
        },
    }
    
    ACCOMMODATION_DATA = {
        "bremen": [
            {"name": "Bremen City Camping", "type": "camping", "price": 15, "amenities": ["showers", "wifi", "bike_storage"], "rating": 4.2},
            {"name": "Bremen Backpackers Hostel", "type": "hostel", "price": 28, "amenities": ["wifi", "kitchen", "bike_storage"], "rating": 4.5},
        ],
        "hamburg": [
            {"name": "Hamburg Beach Camp", "type": "camping", "price": 18, "amenities": ["showers", "wifi", "laundry"], "rating": 4.0},
            {"name": "St. Pauli Hostel", "type": "hostel", "price": 32, "amenities": ["wifi", "bar", "bike_storage"], "rating": 4.6},
        ],
        "lübeck": [
            {"name": "Lübeck Campsite", "type": "camping", "price": 16, "amenities": ["showers", "bike_storage"], "rating": 3.9},
            {"name": "Altstadt Hostel", "type": "hostel", "price": 30, "amenities": ["wifi", "kitchen", "bike_rental"], "rating": 4.4},
        ],
    }
    
    WEATHER_DATA = {
        ("june", "amsterdam"): {"high": 20, "low": 12, "precip": 68, "conditions": "Mild with occasional rain"},
        ("june", "copenhagen"): {"high": 20, "low": 11, "precip": 51, "conditions": "Pleasant with light winds"},
        ("june", "hamburg"): {"high": 21, "low": 12, "precip": 72, "conditions": "Warm with occasional showers"},
    }
    
    ELEVATION_DATA = {
        "amsterdam-bremen": {"gain": 120, "loss": 110, "max": 45, "difficulty": "easy"},
        "bremen-hamburg": {"gain": 180, "loss": 170, "max": 65, "difficulty": "easy"},
        "hamburg-lübeck": {"gain": 240, "loss": 230, "max": 82, "difficulty": "moderate"},
        "lübeck-copenhagen": {"gain": 350, "loss": 340, "max": 125, "difficulty": "moderate"},
    }
    
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        """Return tool definitions in Claude's expected format."""
        return [
            {
                "name": "get_route",
                "description": "Get cycling route information between two cities including distance, estimated days, and waypoints. Returns detailed route data for planning multi-day trips.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "description": "Starting city name"
                        },
                        "end": {
                            "type": "string",
                            "description": "Destination city name"
                        },
                        "daily_distance_km": {
                            "type": "number",
                            "description": "Average daily cycling distance in kilometers",
                            "default": 80
                        }
                    },
                    "required": ["start", "end"]
                }
            },
            {
                "name": "find_accommodation",
                "description": "Find accommodation options near a location. Can filter by type (camping, hostel, hotel) and returns details including price, amenities, and ratings.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City or area to search for accommodation"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["camping", "hostel", "hotel", "any"],
                            "description": "Type of accommodation preferred",
                            "default": "any"
                        },
                        "max_distance_km": {
                            "type": "number",
                            "description": "Maximum distance from route in kilometers",
                            "default": 5
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_weather",
                "description": "Get typical weather information for a location and month, including temperature, precipitation, and cycling suitability assessment.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City or region name"
                        },
                        "month": {
                            "type": "string",
                            "description": "Month name (e.g., 'June', 'September')"
                        }
                    },
                    "required": ["location", "month"]
                }
            },
            {
                "name": "get_elevation_profile",
                "description": "Get terrain difficulty and elevation information for a route segment, including total elevation gain/loss and difficulty rating.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "description": "Starting location"
                        },
                        "end": {
                            "type": "string",
                            "description": "Ending location"
                        }
                    },
                    "required": ["start", "end"]
                }
            },
            {
                "name": "get_points_of_interest",
                "description": "Find interesting places to visit along the route such as historical sites, scenic viewpoints, or local attractions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City or area to search"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["historical", "scenic", "cultural", "food", "any"],
                            "description": "Type of point of interest",
                            "default": "any"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
    
    @staticmethod
    def get_route(start: str, end: str, daily_distance_km: float = 80) -> Dict[str, Any]:
        """Get route information between two points."""
        start_normalized = start.lower()
        end_normalized = end.lower()
        
        # Try to find route in mock data
        route_key = (start_normalized, end_normalized)
        if route_key in CyclingTools.ROUTE_DATA:
            data = CyclingTools.ROUTE_DATA[route_key]
            estimated_days = max(1, int(data["distance_km"] / daily_distance_km))
            
            return {
                "start": start,
                "end": end,
                "distance_km": data["distance_km"],
                "estimated_days": estimated_days,
                "waypoints": data["waypoints"],
                "description": data["description"]
            }
        
        # Fallback for unknown routes
        mock_distance = 400 + (len(start) + len(end)) * 10
        estimated_days = max(1, int(mock_distance / daily_distance_km))
        
        return {
            "start": start,
            "end": end,
            "distance_km": mock_distance,
            "estimated_days": estimated_days,
            "waypoints": [start, f"Mid-point near {start}", end],
            "description": f"Cycling route from {start} to {end}"
        }
    
    @staticmethod
    def find_accommodation(location: str, type: str = "any", max_distance_km: float = 5) -> List[Dict[str, Any]]:
        """Find accommodation near a location."""
        location_normalized = location.lower()
        
        # Get accommodations from mock data
        accommodations = CyclingTools.ACCOMMODATION_DATA.get(location_normalized, [])
        
        # Filter by type if specified
        if type != "any":
            accommodations = [a for a in accommodations if a["type"] == type]
        
        # If no data, generate mock accommodation
        if not accommodations:
            accommodations = [
                {
                    "name": f"{location} Campsite",
                    "type": "camping",
                    "price": 15,
                    "amenities": ["showers", "bike_storage"],
                    "rating": 4.0
                },
                {
                    "name": f"{location} Hostel",
                    "type": "hostel",
                    "price": 30,
                    "amenities": ["wifi", "kitchen", "bike_storage"],
                    "rating": 4.3
                }
            ]
        
        # Format results
        results = []
        for acc in accommodations:
            results.append({
                "name": acc["name"],
                "type": acc["type"],
                "location": location,
                "price_per_night": acc["price"],
                "distance_from_route_km": 1.5,
                "amenities": acc["amenities"],
                "rating": acc.get("rating")
            })
        
        return results
    
    @staticmethod
    def get_weather(location: str, month: str) -> Dict[str, Any]:
        """Get weather information for a location and month."""
        weather_key = (month.lower(), location.lower())
        
        if weather_key in CyclingTools.WEATHER_DATA:
            data = CyclingTools.WEATHER_DATA[weather_key]
        else:
            # Generate mock weather data
            data = {
                "high": 18 + (len(location) % 8),
                "low": 10 + (len(month) % 6),
                "precip": 50 + (len(location) * 3) % 40,
                "conditions": "Generally pleasant cycling weather"
            }
        
        # Assess cycling suitability
        if data["precip"] > 80:
            suitability = "Good but bring rain gear - expect wet days"
        elif data["high"] > 25:
            suitability = "Excellent - warm and mostly dry"
        else:
            suitability = "Good - mild temperatures ideal for cycling"
        
        return {
            "location": location,
            "month": month,
            "avg_temp_high": data["high"],
            "avg_temp_low": data["low"],
            "precipitation_mm": data["precip"],
            "conditions": data["conditions"],
            "cycling_suitability": suitability
        }
    
    @staticmethod
    def get_elevation_profile(start: str, end: str) -> Dict[str, Any]:
        """Get elevation profile for a route segment."""
        route_key = f"{start.lower()}-{end.lower()}"
        
        if route_key in CyclingTools.ELEVATION_DATA:
            data = CyclingTools.ELEVATION_DATA[route_key]
        else:
            # Generate mock elevation data
            base_gain = 150 + (len(start) + len(end)) * 5
            data = {
                "gain": base_gain,
                "loss": base_gain - 20,
                "max": 50 + base_gain // 3,
                "difficulty": "moderate"
            }
        
        descriptions = {
            "easy": "Mostly flat terrain with gentle rolling hills",
            "moderate": "Some hills with moderate climbs, manageable for most cyclists",
            "challenging": "Significant elevation changes with steep sections",
            "difficult": "Very hilly terrain with long, steep climbs"
        }
        
        return {
            "location": f"{start} to {end}",
            "total_elevation_gain_m": data["gain"],
            "total_elevation_loss_m": data["loss"],
            "max_elevation_m": data["max"],
            "difficulty_rating": data["difficulty"],
            "description": descriptions[data["difficulty"]]
        }
    
    @staticmethod
    def get_points_of_interest(location: str, type: str = "any") -> List[Dict[str, Any]]:
        """Get points of interest near a location."""
        # Mock POI data
        pois = [
            {
                "name": f"{location} Old Town",
                "type": "historical",
                "description": "Historic city center with medieval architecture",
                "distance_from_route_km": 0.5
            },
            {
                "name": f"{location} Waterfront",
                "type": "scenic",
                "description": "Beautiful waterfront area perfect for photos",
                "distance_from_route_km": 1.0
            },
            {
                "name": f"Local Brewery near {location}",
                "type": "food",
                "description": "Traditional brewery with local specialties",
                "distance_from_route_km": 2.0
            }
        ]
        
        if type != "any":
            pois = [p for p in pois if p["type"] == type]
        
        return [
            {
                "name": poi["name"],
                "type": poi["type"],
                "location": location,
                "description": poi["description"],
                "distance_from_route_km": poi["distance_from_route_km"]
            }
            for poi in pois
        ]
    
    @staticmethod
    def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool by name with given input."""
        tool_map = {
            "get_route": CyclingTools.get_route,
            "find_accommodation": CyclingTools.find_accommodation,
            "get_weather": CyclingTools.get_weather,
            "get_elevation_profile": CyclingTools.get_elevation_profile,
            "get_points_of_interest": CyclingTools.get_points_of_interest,
        }
        
        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return tool_map[tool_name](**tool_input)
