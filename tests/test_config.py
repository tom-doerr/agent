"""Tests for configuration management."""

import pytest
import tempfile
import os
from pathlib import Path
from pydantic import ValidationError

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    WeatherLocation, WeatherConfig, SmartThingsConfig,
    MLflowConfig, ModelConfig, AgentConfig,
    load_config, save_config, get_config, set_config
)


class TestWeatherConfig:
    def test_weather_location_validation(self):
        """Test weather location validation."""
        # Valid location
        loc = WeatherLocation(
            lat=48.2667,
            lon=10.9833,
            city="Mering",
            region="Bavaria",
            country="Germany"
        )
        assert loc.lat == 48.2667
        assert loc.city == "Mering"
        
        # Missing required field
        with pytest.raises(ValidationError):
            WeatherLocation(lat=48.2667, lon=10.9833)  # Missing city
    
    def test_weather_config(self):
        """Test weather configuration."""
        config = WeatherConfig(
            enabled=True,
            location=WeatherLocation(
                lat=48.2667,
                lon=10.9833,
                city="Mering"
            )
        )
        assert config.enabled is True
        assert config.location.city == "Mering"


class TestSmartThingsConfig:
    def test_token_validation(self):
        """Test SmartThings token validation."""
        # Valid tokens
        config1 = SmartThingsConfig(token="Bearer abc123def456ghi789jkl")
        assert config1.token.startswith("Bearer")
        
        config2 = SmartThingsConfig(token="pat_verylongtokenstring1234567890")
        assert config2.token.startswith("pat")
        
        # Too short token
        with pytest.raises(ValidationError):
            SmartThingsConfig(token="short")


class TestMLflowConfig:
    def test_uri_validation(self):
        """Test MLflow URI validation."""
        # Valid URIs
        config1 = MLflowConfig(tracking_uri="http://localhost:5000")
        config2 = MLflowConfig(tracking_uri="https://mlflow.example.com")
        config3 = MLflowConfig(tracking_uri="file:///path/to/mlruns")
        
        # Invalid URI
        with pytest.raises(ValidationError):
            MLflowConfig(tracking_uri="not-a-uri")


class TestModelConfig:
    def test_model_config_validation(self):
        """Test model configuration validation."""
        # Valid config
        config = ModelConfig(
            default_model="gpt-4",
            max_tokens=2000,
            temperature=0.8
        )
        assert config.max_tokens == 2000
        
        # Invalid max_tokens
        with pytest.raises(ValidationError):
            ModelConfig(max_tokens=50)  # Too small
        
        with pytest.raises(ValidationError):
            ModelConfig(max_tokens=200000)  # Too large
        
        # Invalid temperature
        with pytest.raises(ValidationError):
            ModelConfig(temperature=3.0)  # Too high


class TestAgentConfig:
    def test_full_config(self):
        """Test complete agent configuration."""
        config = AgentConfig(
            weather=WeatherConfig(
                enabled=True,
                location=WeatherLocation(
                    lat=48.2667,
                    lon=10.9833,
                    city="Mering"
                )
            ),
            mlflow=MLflowConfig(tracking_uri="http://localhost:5002"),
            model=ModelConfig(default_model="deepseek-reasoner", max_tokens=5000)
        )
        
        assert config.weather.location.city == "Mering"
        assert config.mlflow.tracking_uri == "http://localhost:5002"
        assert config.model.max_tokens == 5000
    
    def test_path_conversion(self):
        """Test that string paths are converted to Path objects."""
        config = AgentConfig(
            data_dir="./data",
            models_dir="./models",
            logs_dir="./logs"
        )
        
        assert isinstance(config.data_dir, Path)
        assert isinstance(config.models_dir, Path)
        assert isinstance(config.logs_dir, Path)
    
    def test_no_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError):
            AgentConfig(extra_field="not allowed")


class TestConfigIO:
    def test_load_save_config(self):
        """Test loading and saving configuration."""
        # Save current env var if it exists
        old_mlflow_uri = os.environ.pop("MLFLOW_TRACKING_URI", None)
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
                # Write test config
                f.write("""
[weather]
enabled = true

[weather.location]
lat = 48.2667
lon = 10.9833
city = "Mering"

[mlflow]
tracking_uri = "http://localhost:5002"
""")
                config_path = Path(f.name)
            
            try:
                # Load config
                config = load_config(config_path)
                assert config.weather.location.city == "Mering"
                assert config.mlflow.tracking_uri == "http://localhost:5002"
                
                # Modify and save
                config.model.max_tokens = 8000
                save_config(config, config_path)
                
                # Reload to verify
                config2 = load_config(config_path)
                assert config2.model.max_tokens == 8000
                
            finally:
                config_path.unlink()
                
        finally:
            # Restore env var if it existed
            if old_mlflow_uri is not None:
                os.environ["MLFLOW_TRACKING_URI"] = old_mlflow_uri
    
    def test_env_override(self):
        """Test environment variable overrides."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""
[weather.location]
lat = 48.1351
lon = 11.5820
city = "Munich"

[smartthings]
token = "old_token_that_is_long_enough_for_validation"
""")
            config_path = Path(f.name)
        
        try:
            # Set environment variables
            os.environ["WEATHER_CITY"] = "Berlin"
            os.environ["SMARTTHINGS_TOKEN"] = "new_token_from_env_that_is_long_enough"
            os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow:5000"
            
            # Load config with env overrides
            config = load_config(config_path)
            
            # Verify overrides
            assert config.weather.location.city == "Berlin"
            assert config.smartthings.token == "new_token_from_env_that_is_long_enough"
            assert config.mlflow.tracking_uri == "http://mlflow:5000"
            
        finally:
            # Clean up
            config_path.unlink()
            os.environ.pop("WEATHER_CITY", None)
            os.environ.pop("SMARTTHINGS_TOKEN", None)
            os.environ.pop("MLFLOW_TRACKING_URI", None)
    
    def test_missing_config_file(self):
        """Test loading when config file doesn't exist."""
        config = load_config("nonexistent.toml")
        
        # Should return defaults
        assert config.weather.enabled is True
        assert config.mlflow.tracking_uri == "http://localhost:5002"


class TestGlobalConfig:
    def test_global_config(self):
        """Test global config instance."""
        # Get initial config
        config1 = get_config()
        assert isinstance(config1, AgentConfig)
        
        # Should return same instance
        config2 = get_config()
        assert config1 is config2
        
        # Set new config
        new_config = AgentConfig(
            model=ModelConfig(default_model="custom-model")
        )
        set_config(new_config)
        
        # Verify it was set
        config3 = get_config()
        assert config3.model.default_model == "custom-model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])