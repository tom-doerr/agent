#!/usr/bin/env python3
"""
Samsung SmartThings API client for home automation control.

Requires:
1. SmartThings Personal Access Token from https://account.smartthings.com/tokens
2. pip install requests
"""

import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path


class SmartThingsClient:
    """Client for Samsung SmartThings API."""
    
    def __init__(self, token: str = None):
        """Initialize with API token from env or config."""
        self.base_url = "https://api.smartthings.com/v1"
        
        # Load token from config or environment
        if not token:
            token = self._load_token()
        
        if not token:
            raise ValueError("SmartThings token required. Set in nlco_config.toml or pass directly.")
        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _load_token(self) -> Optional[str]:
        """Load token from config file."""
        import os
        
        # Check environment variable first
        token = os.environ.get("SMARTTHINGS_TOKEN")
        if token:
            return token
        
        # Check config file
        if Path("nlco_config.toml").exists():
            try:
                import toml
                config = toml.load("nlco_config.toml")
                return config.get("smartthings", {}).get("token")
            except:
                pass
        
        return None
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make API request."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    # Discovery methods
    def get_locations(self) -> List[Dict]:
        """Get all locations (homes)."""
        return self._request("GET", "locations")["items"]
    
    def get_rooms(self, location_id: str) -> List[Dict]:
        """Get all rooms in a location."""
        return self._request("GET", f"locations/{location_id}/rooms")["items"]
    
    def get_devices(self) -> List[Dict]:
        """Get all devices."""
        return self._request("GET", "devices")["items"]
    
    def get_device(self, device_id: str) -> Dict:
        """Get device details and current status."""
        return self._request("GET", f"devices/{device_id}/status")
    
    # Control methods
    def execute_command(self, device_id: str, commands: List[Dict]) -> Dict:
        """
        Execute commands on a device.
        
        Example commands:
        - Turn on: [{"capability": "switch", "command": "on"}]
        - Set level: [{"capability": "switchLevel", "command": "setLevel", "arguments": [50]}]
        - Set color: [{"capability": "colorControl", "command": "setColor", "arguments": [{"hex": "#FF0000"}]}]
        """
        data = {"commands": commands}
        return self._request("POST", f"devices/{device_id}/commands", data)
    
    # Convenience methods
    def turn_on(self, device_id: str):
        """Turn device on."""
        return self.execute_command(device_id, [{"capability": "switch", "command": "on"}])
    
    def turn_off(self, device_id: str):
        """Turn device off."""
        return self.execute_command(device_id, [{"capability": "switch", "command": "off"}])
    
    def set_level(self, device_id: str, level: int):
        """Set dimmer level (0-100)."""
        return self.execute_command(device_id, [
            {"capability": "switchLevel", "command": "setLevel", "arguments": [level]}
        ])
    
    def set_temperature(self, device_id: str, temperature: float):
        """Set thermostat temperature."""
        return self.execute_command(device_id, [
            {"capability": "thermostatCoolingSetpoint", "command": "setCoolingSetpoint", "arguments": [temperature]}
        ])
    
    def get_device_by_name(self, name: str) -> Optional[Dict]:
        """Find device by name."""
        devices = self.get_devices()
        for device in devices:
            if device.get("label", "").lower() == name.lower():
                return device
        return None
    
    def list_device_capabilities(self, device_id: str) -> List[str]:
        """List all capabilities of a device."""
        device = self._request("GET", f"devices/{device_id}")
        return [cap["id"] for cap in device.get("components", [{}])[0].get("capabilities", [])]


def main():
    """Example usage and device discovery."""
    import sys
    
    client = SmartThingsClient()
    
    if len(sys.argv) < 2:
        print("SmartThings CLI")
        print("\nUsage:")
        print("  python smartthings_client.py list              - List all devices")
        print("  python smartthings_client.py status <device>   - Get device status")
        print("  python smartthings_client.py on <device>       - Turn device on")
        print("  python smartthings_client.py off <device>      - Turn device off")
        print("  python smartthings_client.py level <device> <0-100> - Set dimmer level")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        print("Devices:")
        for device in client.get_devices():
            print(f"  {device['label']} (ID: {device['deviceId']})")
            caps = client.list_device_capabilities(device['deviceId'])
            print(f"    Capabilities: {', '.join(caps[:5])}...")
    
    elif command == "status" and len(sys.argv) > 2:
        device_name = " ".join(sys.argv[2:])
        device = client.get_device_by_name(device_name)
        if device:
            status = client.get_device(device['deviceId'])
            print(f"Status of {device['label']}:")
            print(json.dumps(status, indent=2))
        else:
            print(f"Device '{device_name}' not found")
    
    elif command == "on" and len(sys.argv) > 2:
        device_name = " ".join(sys.argv[2:])
        device = client.get_device_by_name(device_name)
        if device:
            client.turn_on(device['deviceId'])
            print(f"Turned on {device['label']}")
        else:
            print(f"Device '{device_name}' not found")
    
    elif command == "off" and len(sys.argv) > 2:
        device_name = " ".join(sys.argv[2:])
        device = client.get_device_by_name(device_name)
        if device:
            client.turn_off(device['deviceId'])
            print(f"Turned off {device['label']}")
        else:
            print(f"Device '{device_name}' not found")
    
    elif command == "level" and len(sys.argv) > 3:
        device_name = " ".join(sys.argv[2:-1])
        level = int(sys.argv[-1])
        device = client.get_device_by_name(device_name)
        if device:
            client.set_level(device['deviceId'], level)
            print(f"Set {device['label']} to {level}%")
        else:
            print(f"Device '{device_name}' not found")


if __name__ == "__main__":
    main()