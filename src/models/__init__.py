"""Pydantic models for data validation."""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message."""
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None
    session_state: Optional[dict] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    response: str
    conversation_id: str
    session_state: dict
    tools_used: List[str] = Field(default_factory=list)
    next_request: Optional[dict] = Field(
        default=None,
        description="Pre-filled template for the next request to continue the conversation"
    )


class RouteInfo(BaseModel):
    """Route information between two points."""
    start: str
    end: str
    distance_km: float
    estimated_days: int
    waypoints: List[str]
    description: str


class Accommodation(BaseModel):
    """Accommodation information."""
    name: str
    type: Literal["camping", "hostel", "hotel"]
    location: str
    price_per_night: float
    distance_from_route_km: float
    amenities: List[str]
    rating: Optional[float] = None


class WeatherInfo(BaseModel):
    """Weather information for a location."""
    location: str
    month: str
    avg_temp_high: float
    avg_temp_low: float
    precipitation_mm: float
    conditions: str
    cycling_suitability: str


class ElevationProfile(BaseModel):
    """Elevation and terrain difficulty information."""
    location: str
    total_elevation_gain_m: float
    total_elevation_loss_m: float
    max_elevation_m: float
    difficulty_rating: Literal["easy", "moderate", "challenging", "difficult"]
    description: str


class PointOfInterest(BaseModel):
    """Point of interest along the route."""
    name: str
    type: str
    location: str
    description: str
    distance_from_route_km: float


class DayPlan(BaseModel):
    """Plan for a single day of cycling."""
    day: int
    start_location: str
    end_location: str
    distance_km: float
    accommodation: Accommodation
    elevation_gain_m: float
    difficulty: str
    highlights: List[str]
    notes: str


class TripPlan(BaseModel):
    """Complete multi-day trip plan."""
    title: str
    start_date: Optional[str] = None
    days: List[DayPlan]
    total_distance_km: float
    total_cost_estimate: float
    weather_summary: str
    packing_suggestions: List[str]
