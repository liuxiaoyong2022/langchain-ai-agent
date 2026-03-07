#!/usr/bin/env python3
"""
Weather MCP Server

This server provides weather-related tools that can be used by LangChain agents
through the Model Context Protocol (MCP) using HTTP transport.

Tools provided:
- get_weather: Get current weather for a location
- get_forecast: Get weather forecast for a location
"""

import sys
import logging
import asyncio
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP
from langchain_core.tools import InjectedToolCallId, tool
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Weather Server")

# Mock weather data for demonstration
MOCK_WEATHER_DATA = {
    "new york": {
        "current": {
            "temperature": 22,
            "condition": "Partly cloudy",
            "humidity": 65,
            "wind_speed": 10,
            "description": "A pleasant day with some clouds"
        },
        "forecast": [
            {"day": "Today", "high": 24, "low": 18, "condition": "Partly cloudy"},
            {"day": "Tomorrow", "high": 26, "low": 20, "condition": "Sunny"},
            {"day": "Day 3", "high": 23, "low": 17, "condition": "Light rain"},
        ]
    },
    "london": {
        "current": {
            "temperature": 15,
            "condition": "Rainy",
            "humidity": 80,
            "wind_speed": 15,
            "description": "Typical London weather with light rain"
        },
        "forecast": [
            {"day": "Today", "high": 16, "low": 12, "condition": "Rainy"},
            {"day": "Tomorrow", "high": 18, "low": 14, "condition": "Cloudy"},
            {"day": "Day 3", "high": 17, "low": 13, "condition": "Partly cloudy"},
        ]
    },
    "tokyo": {
        "current": {
            "temperature": 28,
            "condition": "Sunny",
            "humidity": 55,
            "wind_speed": 8,
            "description": "Clear skies and warm temperature"
        },
        "forecast": [
            {"day": "Today", "high": 30, "low": 24, "condition": "Sunny"},
            {"day": "Tomorrow", "high": 32, "low": 26, "condition": "Hot"},
            {"day": "Day 3", "high": 29, "low": 23, "condition": "Partly cloudy"},
        ]
    }
}

@tool()
def get_weather(location: str) -> str:
    """Get current weather information for a specified location.
    
    Args:
        location: The location to get weather for (e.g., "New York", "London")
        
    Returns:
        Current weather information as a formatted string
    """
    location_key = location.lower().strip()
    
    if location_key not in MOCK_WEATHER_DATA:
        available_locations = ", ".join(MOCK_WEATHER_DATA.keys())
        return f"Weather data not available for '{location}'. Available locations: {available_locations}"
    
    weather = MOCK_WEATHER_DATA[location_key]["current"]
    
    result = f"""Current Weather for {location.title()}:
    🌡️Temperature: {weather['temperature']}°C
   ☁️Condition: {weather['condition']}
   💧Humidity: {weather['humidity']}%
   💨Wind Speed: {weather['wind_speed']} km/h
   📝Description: {weather['description']}"""
    
    logger.info(f"Weather request for {location}: {weather['condition']}, {weather['temperature']}°C")
    print(f"weather result:----->{result}")
    # print(f"weather ----->:{weather}")
    return result

@tool()
def get_forecast(location: str, days: int = 3) -> str:
    """Get weather forecast for a specified location.
    
    Args:
        location: The location to get forecast for
        days: Number of days to forecast (1-3, default 3)
        
    Returns:
        Weather forecast as a formatted string
    """
    location_key = location.lower().strip()
    
    if location_key not in MOCK_WEATHER_DATA:
        available_locations = ", ".join(MOCK_WEATHER_DATA.keys())
        return f"Weather data not available for '{location}'. Available locations: {available_locations}"
    
    # Limit days to available forecast data
    days = min(max(1, days), 3)
    
    forecast_data = MOCK_WEATHER_DATA[location_key]["forecast"][:days]
    
    result = f"Weather Forecast for {location.title()} ({days} days):\n\n"
    
    for day_data in forecast_data:
        result += f"📅 {day_data['day']}:\n"
        result += f"   🌡️  High: {day_data['high']}°C, Low: {day_data['low']}°C\n"
        result += f"   ☁️  Condition: {day_data['condition']}\n\n"
    
    logger.info(f"Forecast request for {location}: {days} days")
    return result.strip()

@tool()
def compare_weather(location1: str, location2: str) -> str:
    """Compare current weather between two locations.
    
    Args:
        location1: First location to compare
        location2: Second location to compare
        
    Returns:
        Weather comparison as a formatted string
    """
    loc1_key = location1.lower().strip()
    loc2_key = location2.lower().strip()
    
    if loc1_key not in MOCK_WEATHER_DATA:
        return f"Weather data not available for '{location1}'"
    
    if loc2_key not in MOCK_WEATHER_DATA:
        return f"Weather data not available for '{location2}'"
    
    weather1 = MOCK_WEATHER_DATA[loc1_key]["current"]
    weather2 = MOCK_WEATHER_DATA[loc2_key]["current"]
    
    temp_diff = weather1["temperature"] - weather2["temperature"]
    temp_comparison = "warmer" if temp_diff > 0 else "cooler" if temp_diff < 0 else "the same temperature"
    
    result = f"""Weather Comparison:

📍 {location1.title()}:
   🌡️  {weather1['temperature']}°C, {weather1['condition']}
   💧 {weather1['humidity']}% humidity

📍 {location2.title()}:
   🌡️  {weather2['temperature']}°C, {weather2['condition']}
   💧 {weather2['humidity']}% humidity

📊 Summary:
   {location1.title()} is {abs(temp_diff):.1f}°C {temp_comparison} than {location2.title()}"""
    
    logger.info(f"Weather comparison: {location1} vs {location2}")
    return result

@tool()
def get_weather_alerts(location: str) -> str:
    """Get weather alerts and warnings for a location.
    
    Args:
        location: The location to check for weather alerts
        
    Returns:
        Weather alerts information
    """
    location_key = location.lower().strip()
    
    # Mock alerts data
    alerts = {
        "new york": [],
        "london": ["Light rain expected throughout the day"],
        "tokyo": ["High temperature warning - stay hydrated"]
    }
    
    if location_key not in alerts:
        return f"No alert data available for '{location}'"
    
    location_alerts = alerts[location_key]
    
    if not location_alerts:
        result = f"No active weather alerts for {location.title()} ✅"
    else:
        result = f"Weather Alerts for {location.title()}:\n"
        for i, alert in enumerate(location_alerts, 1):
            result += f"⚠️  Alert {i}: {alert}\n"
    
    logger.info(f"Weather alerts check for {location}")
    return result.strip()

def main():
    """Main function to run the MCP server."""
    logger.info("Starting Weather MCP Server...")
    logger.info("Available tools: get_weather, get_forecast, compare_weather, get_weather_alerts")
    logger.info("Server running on streamable-http transport...")
    
    try:
        # Run the server using streamable-http transport
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 