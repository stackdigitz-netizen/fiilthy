"""
Demo Mode Configuration System
Provides centralized control for switching between demo and production modes
"""

import os
from enum import Enum
from typing import Dict, Any


class Environment(str, Enum):
    DEMO = "demo"
    PRODUCTION = "production"


class DemoConfig:
    """Centralized configuration for demo vs production mode"""
    
    def __init__(self):
        # Get from environment variable, default to demo for safety
        self.environment = os.getenv("APP_ENVIRONMENT", "demo").lower()
        self.demo_mode = self.environment == "demo"
        
    @property
    def is_demo(self) -> bool:
        """Check if running in demo mode"""
        return self.demo_mode
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.demo_mode
    
    def set_environment(self, environment: str):
        """Change environment at runtime"""
        self.environment = environment.lower()
        self.demo_mode = self.environment == "demo"
    
    def get_demo_settings(self) -> Dict[str, Any]:
        """Get all demo mode settings"""
        return {
            "environment": self.environment,
            "is_demo": self.demo_mode,
            "is_production": self.is_production,
            "demo_features": {
                "api_calls": False,  # Don't call real APIs
                "database_persistence": True,  # Still save to DB
                "realistic_delays": True,  # Simulate processing time
                "generate_synthetic_data": True,  # Create realistic test data
            }
        }


# Global instance
demo_config = DemoConfig()
