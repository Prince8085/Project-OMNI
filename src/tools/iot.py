"""
IoT / Smart Home Module for OMNI.
Connects to Home Assistant via REST API or MQTT.
"""

import logging
import requests
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SmartHome:
    def __init__(self):
        # Load config from env
        self.ha_url = os.getenv("HOME_ASSISTANT_URL", "http://homeassistant.local:8123")
        self.ha_token = os.getenv("HOME_ASSISTANT_TOKEN", "")
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        
        self.headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json",
        }
        
        if not self.ha_token:
            logger.warning("Home Assistant Token not found. IoT disabled.")
            self.is_active = False
        else:
            self.is_active = True
            logger.info(f"IoT Module connected to {self.ha_url}")

    def get_state(self, entity_id: str) -> str:
        """Get the state of an entity."""
        if not self.is_active: return "IoT Disabled"
        
        try:
            url = f"{self.ha_url}/api/states/{entity_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("state", "Unknown")
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"

    def call_service(self, domain: str, service: str, entity_id: str) -> str:
        """Call a service (e.g., light.turn_on)."""
        if not self.is_active: return "IoT Disabled"
        
        try:
            url = f"{self.ha_url}/api/services/{domain}/{service}"
            data = {"entity_id": entity_id}
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                return f"Successfully called {domain}.{service} on {entity_id}"
            return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error: {e}"

    def turn_on(self, entity_id: str):
        return self.call_service(entity_id.split('.')[0], "turn_on", entity_id)

    def turn_off(self, entity_id: str):
        return self.call_service(entity_id.split('.')[0], "turn_off", entity_id)
