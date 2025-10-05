"""Configuration management with Pydantic validation."""

from pathlib import Path
from typing import Optional, Union
import os
import toml

from pydantic import BaseModel, Field, validator


class WeatherLocation(BaseModel):
    """Weather location configuration."""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude") 
    city: str = Field(..., description="City name")
    region: Optional[str] = Field(None, description="Region/state")
    country: Optional[str] = Field(None, description="Country name")


class WeatherConfig(BaseModel):
    """Weather configuration."""
    enabled: bool = Field(True, description="Enable weather information")
    location: Optional[WeatherLocation] = None


class SmartThingsConfig(BaseModel):
    """SmartThings configuration."""
    token: Optional[str] = Field(None, description="SmartThings API token")
    
    @validator('token')
    def validate_token(cls, v):
        if v and not v.startswith(('Bearer', 'pat')):
            # Just a basic check - real token validation would require API call
            if len(v) < 20:
                raise ValueError("Token appears too short")
        return v


class MLflowConfig(BaseModel):
    """MLflow configuration."""
    tracking_uri: str = Field("http://localhost:5002", description="MLflow tracking server URI")
    experiment_name: str = Field("default", description="Default experiment name")
    
    @validator('tracking_uri')
    def validate_uri(cls, v):
        if not (v.startswith('http://') or v.startswith('https://') or v.startswith('file://')):
            raise ValueError("tracking_uri must be a valid URI")
        return v


class ModelConfig(BaseModel):
    """Model configuration."""
    default_model: str = Field("deepseek/deepseek-reasoner", description="Default LLM model")
    max_tokens: int = Field(4000, description="Maximum tokens for generation")
    temperature: float = Field(0.7, description="Temperature for generation", ge=0.0, le=2.0)
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v < 100:
            raise ValueError("max_tokens must be at least 100")
        if v > 100000:
            raise ValueError("max_tokens cannot exceed 100000")
        return v


class SocialMediaConfig(BaseModel):
    """Social media/post queue configuration."""
    post_queue_path: Optional[Path] = Field(
        None, description="Path to the saved posts queue JSON file"
    )
    posted_posts_path: Optional[Path] = Field(
        None, description="Path to the posted posts JSON file for autoposter health checks"
    )

    @validator('post_queue_path', pre=True)
    def convert_to_path(cls, v):
        if v in (None, ""):
            return None
        return Path(v)

    @validator('posted_posts_path', pre=True)
    def convert_posted_path(cls, v):
        if v in (None, ""):
            return None
        return Path(v)


class AgentConfig(BaseModel):
    """Main configuration for the agent system."""
    weather: WeatherConfig = Field(default_factory=WeatherConfig)
    smartthings: SmartThingsConfig = Field(default_factory=SmartThingsConfig)
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    social: SocialMediaConfig = Field(default_factory=SocialMediaConfig)
    
    # Paths
    data_dir: Path = Field(Path("."), description="Data directory")
    models_dir: Path = Field(Path("models"), description="Models directory")
    logs_dir: Path = Field(Path("logs"), description="Logs directory")
    
    @validator('data_dir', 'models_dir', 'logs_dir', pre=True)
    def convert_to_path(cls, v):
        return Path(v)
    
    class Config:
        extra = "forbid"  # Don't allow extra fields


def load_config(config_path: Union[str, Path] = "nlco_config.toml") -> AgentConfig:
    """
    Load configuration from TOML file with validation.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Validated AgentConfig instance
    """
    config_path = Path(config_path)
    
    # Start with defaults
    config_dict = {}
    
    # Load from file if it exists
    if config_path.exists():
        with open(config_path) as f:
            config_dict = toml.load(f)
    
    # Override with environment variables
    env_overrides = {}
    
    # Weather location from env
    if os.getenv("WEATHER_CITY"):
        # Only override city if location already exists
        if "weather" in config_dict and "location" in config_dict["weather"]:
            env_overrides.setdefault("weather", {}).setdefault("location", config_dict["weather"]["location"].copy())
            env_overrides["weather"]["location"]["city"] = os.getenv("WEATHER_CITY")
    
    # SmartThings token from env
    if os.getenv("SMARTTHINGS_TOKEN"):
        env_overrides.setdefault("smartthings", {})
        env_overrides["smartthings"]["token"] = os.getenv("SMARTTHINGS_TOKEN")
    
    # MLflow URI from env
    if os.getenv("MLFLOW_TRACKING_URI"):
        env_overrides.setdefault("mlflow", {})
        env_overrides["mlflow"]["tracking_uri"] = os.getenv("MLFLOW_TRACKING_URI")
    
    # Merge env overrides
    for key, value in env_overrides.items():
        if key in config_dict:
            config_dict[key].update(value)
        else:
            config_dict[key] = value
    
    # Create and validate config
    return AgentConfig(**config_dict)


def save_config(config: AgentConfig, config_path: Union[str, Path] = "nlco_config.toml"):
    """
    Save configuration to TOML file.
    
    Args:
        config: AgentConfig instance to save
        config_path: Path to save configuration
    """
    config_path = Path(config_path)
    
    # Convert to dict, handling Path objects
    config_dict = config.dict()

    def _convert_paths(obj):
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, dict):
            return {k: _convert_paths(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_convert_paths(v) for v in obj]
        return obj

    config_dict = _convert_paths(config_dict)
    
    # Remove None values for cleaner TOML
    def remove_none(d):
        if isinstance(d, dict):
            return {k: remove_none(v) for k, v in d.items() if v is not None}
        return d
    
    config_dict = remove_none(config_dict)
    
    # Save to file
    with open(config_path, 'w') as f:
        toml.dump(config_dict, f)


# Global config instance (lazy loaded)
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: AgentConfig):
    """Set the global configuration instance."""
    global _config
    _config = config
