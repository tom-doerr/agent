"""Simple home automation functions for context integration."""

from smartthings_client import SmartThingsClient
from typing import List, Dict, Optional


def get_home_status() -> str:
    """Get current status of key home devices for context."""
    try:
        client = SmartThingsClient()
        
        status_lines = ["Home devices:"]
        
        # Get all devices
        devices = client.get_devices()
        
        # Group by type
        lights = []
        thermostats = []
        sensors = []
        other = []
        
        for device in devices:
            caps = client.list_device_capabilities(device['deviceId'])
            device_status = client.get_device(device['deviceId'])
            
            if 'switch' in caps or 'switchLevel' in caps:
                # Light or switch
                power = device_status.get('components', {}).get('main', {}).get('switch', {}).get('switch', {}).get('value', 'unknown')
                level = device_status.get('components', {}).get('main', {}).get('switchLevel', {}).get('level', {}).get('value')
                
                if level:
                    lights.append(f"{device['label']}: {power} ({level}%)")
                else:
                    lights.append(f"{device['label']}: {power}")
            
            elif 'thermostat' in caps:
                # Thermostat
                temp = device_status.get('components', {}).get('main', {}).get('temperatureMeasurement', {}).get('temperature', {}).get('value', '?')
                setpoint = device_status.get('components', {}).get('main', {}).get('thermostatCoolingSetpoint', {}).get('coolingSetpoint', {}).get('value', '?')
                thermostats.append(f"{device['label']}: {temp}°C (set: {setpoint}°C)")
            
            elif 'temperatureMeasurement' in caps or 'relativeHumidityMeasurement' in caps:
                # Sensor
                temp = device_status.get('components', {}).get('main', {}).get('temperatureMeasurement', {}).get('temperature', {}).get('value')
                humidity = device_status.get('components', {}).get('main', {}).get('relativeHumidityMeasurement', {}).get('humidity', {}).get('value')
                
                if temp and humidity:
                    sensors.append(f"{device['label']}: {temp}°C, {humidity}%")
                elif temp:
                    sensors.append(f"{device['label']}: {temp}°C")
            
            else:
                other.append(device['label'])
        
        # Format output
        if lights:
            status_lines.append(f"  Lights: {', '.join(lights[:3])}")
        if thermostats:
            status_lines.append(f"  Climate: {', '.join(thermostats)}")
        if sensors:
            status_lines.append(f"  Sensors: {', '.join(sensors[:2])}")
        
        return "\n".join(status_lines)
        
    except Exception as e:
        return f"Home devices: unavailable (no token configured?)"


def execute_home_command(command: str) -> str:
    """Execute a simple home automation command."""
    try:
        client = SmartThingsClient()
        
        # Parse simple commands
        cmd_lower = command.lower()
        
        if "turn on" in cmd_lower:
            device_name = cmd_lower.replace("turn on", "").strip()
            device = client.get_device_by_name(device_name)
            if device:
                client.turn_on(device['deviceId'])
                return f"Turned on {device['label']}"
            return f"Device '{device_name}' not found"
        
        elif "turn off" in cmd_lower:
            device_name = cmd_lower.replace("turn off", "").strip()
            device = client.get_device_by_name(device_name)
            if device:
                client.turn_off(device['deviceId'])
                return f"Turned off {device['label']}"
            return f"Device '{device_name}' not found"
        
        elif "set" in cmd_lower and "%" in cmd_lower:
            # Extract device and level
            parts = cmd_lower.replace("set", "").replace("%", "").strip().split()
            if parts:
                level = int(parts[-1])
                device_name = " ".join(parts[:-1])
                device = client.get_device_by_name(device_name)
                if device:
                    client.set_level(device['deviceId'], level)
                    return f"Set {device['label']} to {level}%"
                return f"Device '{device_name}' not found"
        
        return "Command not understood. Try: 'turn on/off <device>' or 'set <device> <level>%'"
        
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Test the functions
    print(get_home_status())