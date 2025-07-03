"""Tests for context_provider module."""

import subprocess
import json
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path

import pytest

# Import the module under test
import sys
sys.path.append(str(Path(__file__).parent.parent))
from context_provider import get_weather_info, get_system_info, create_context_string


class TestGetWeatherInfo:
    @patch('subprocess.run')
    def test_weather_info_success(self, mock_run):
        """Test successful weather API call."""
        # Mock weather API response
        mock_weather_data = {
            "current_condition": [{
                "weatherDesc": [{"value": "Sunny"}],
                "temp_C": "25",
                "FeelsLikeC": "27",
                "humidity": "45",
                "windspeedKmph": "10"
            }],
            "weather": [
                {},  # Today
                {   # Tomorrow
                    "maxtempC": "28",
                    "mintempC": "18",
                    "hourly": [
                        {}, {}, {}, {},
                        {"weatherDesc": [{"value": "Partly cloudy"}]}
                    ]
                }
            ]
        }
        
        mock_run.return_value.stdout = json.dumps(mock_weather_data)
        
        result = get_weather_info()
        
        assert "Sunny 25°C" in result
        assert "feels:27°C" in result
        assert "humidity:45%" in result
        assert "wind:10km/h" in result
        assert "Tomorrow: Partly cloudy 28°/18°C" in result
    
    @patch('subprocess.run')
    def test_weather_info_failure(self, mock_run):
        """Test weather API failure."""
        mock_run.side_effect = Exception("Network error")
        
        result = get_weather_info()
        
        assert "unavailable" in result
    
    @patch('subprocess.run')
    def test_weather_info_invalid_json(self, mock_run):
        """Test invalid JSON response."""
        mock_run.return_value.stdout = "invalid json"
        
        result = get_weather_info()
        
        assert "unavailable" in result


class TestGetSystemInfo:
    @patch('subprocess.run')
    def test_system_info(self, mock_run):
        """Test system info gathering."""
        # Mock free command output
        mock_free_output = """              total        used        free      shared  buff/cache   available
Mem:            15Gi       5.2Gi       1.3Gi       1.0Gi       8.9Gi       8.8Gi
Swap:          2.0Gi       0.0Gi       2.0Gi"""
        
        # Mock df command output
        mock_df_output = """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       234G  156G   67G  71% /"""
        
        # Set up mock responses in order
        mock_run.side_effect = [
            Mock(stdout=mock_free_output),
            Mock(stdout=mock_df_output)
        ]
        
        result = get_system_info()
        
        assert "'free -h':" in result
        assert "15Gi" in result  # Total memory
        assert "'df -h /':" in result
        assert "234G" in result  # Disk size
        assert mock_run.call_count == 2


class TestCreateContextString:
    @patch('context_provider.get_weather_info')
    @patch('context_provider.get_system_info')
    def test_create_context_string(self, mock_system, mock_weather):
        """Test full context string creation."""
        # Mock weather and system info
        mock_weather.return_value = "Mering: Sunny 25°C"
        mock_system.return_value = "System info here"
        
        result = create_context_string()
        
        # Check all components are present
        assert "Datetime:" in result
        assert "Weather: Mering: Sunny 25°C" in result
        assert "System info here" in result
        
        # Verify it includes a real datetime (format check)
        import re
        assert re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', result)


class TestConfigLoading:
    @patch('pathlib.Path.exists')
    @patch('toml.load')
    def test_config_loading_success(self, mock_toml_load, mock_exists):
        """Test successful config loading."""
        mock_exists.return_value = True
        mock_toml_load.return_value = {
            "weather": {
                "location": {
                    "city": "Munich"
                }
            }
        }
        
        # Need to reload the module to test config loading
        import importlib
        import context_provider
        importlib.reload(context_provider)
        
        assert context_provider.LOCATION == "Munich"
    
    @patch('pathlib.Path.exists')
    def test_config_missing(self, mock_exists):
        """Test behavior when config file doesn't exist."""
        mock_exists.return_value = False
        
        import importlib
        import context_provider
        importlib.reload(context_provider)
        
        assert context_provider.LOCATION == "Mering"  # Default


class TestIntegration:
    def test_real_context_creation(self):
        """Integration test - actually create context (without weather API)."""
        # This will use real system commands but mock weather to avoid network calls
        with patch('context_provider.get_weather_info', return_value="Weather mocked"):
            result = create_context_string()
            
            # Should have all components
            assert "Datetime:" in result
            assert "Weather: Weather mocked" in result
            assert "Mem:" in result  # From free command
            assert "Filesystem" in result  # From df command


if __name__ == "__main__":
    pytest.main([__file__, "-v"])