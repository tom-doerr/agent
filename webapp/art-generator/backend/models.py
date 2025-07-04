from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ImageProvider(str, Enum):
    OPENAI = "openai"
    REPLICATE = "replicate"
    LOCAL = "local"
    MOCK = "mock"


class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    provider: ImageProvider = ImageProvider.OPENAI
    negative_prompt: Optional[str] = None
    num_images: int = Field(1, ge=1, le=4)
    size: str = Field("1024x1024", pattern="^[0-9]+x[0-9]+$")
    style: Optional[str] = None


class GeneratedImage(BaseModel):
    id: str
    url: str
    prompt: str
    provider: ImageProvider
    latent_vector: List[float]  # Embedding representation
    created_at: datetime
    metadata: Dict[str, Any] = {}


class PreferenceComparison(BaseModel):
    winner_id: str
    loser_id: str
    comparison_type: str = "a_b_test"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserPreference(BaseModel):
    image_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    feedback_type: str = "rating"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RankingUpdate(BaseModel):
    image_rankings: List[str]  # Ordered list of image IDs from best to worst


class PreferencePrediction(BaseModel):
    image_id: str
    predicted_score: float
    confidence: float


class GenerationStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float = Field(0.0, ge=0.0, le=1.0)
    result: Optional[GeneratedImage] = None
    error: Optional[str] = None