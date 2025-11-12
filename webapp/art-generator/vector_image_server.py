#!/usr/bin/env python3
"""
Vector Embedding to Image Generation Server

This server provides an API to generate images directly from vector embeddings,
bypassing the need for text prompts. It supports multiple generation methods:
1. Direct latent space manipulation
2. VAE decoder for reconstruction
3. Guided diffusion from embeddings
"""

import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime
import base64
import io

import torch
import torch.nn as nn
from PIL import Image
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LATENT_DIM = 512
IMAGE_SIZE = 512
CHANNELS = 3


class VectorRequest(BaseModel):
    """Request model for vector-based image generation"""
    vector: List[float] = Field(..., description="Embedding vector")
    size: Optional[int] = Field(512, description="Output image size")
    method: Optional[str] = Field("vae", description="Generation method: vae, gan, diffusion")
    strength: Optional[float] = Field(1.0, description="Generation strength (0-1)")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    

class ImageResponse(BaseModel):
    """Response model for generated images"""
    image: str = Field(..., description="Base64 encoded image")
    method: str = Field(..., description="Generation method used")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimpleVAE(nn.Module):
    """Simple Variational Autoencoder for vector to image generation"""
    
    def __init__(self, latent_dim: int = 512, image_size: int = 512):
        super().__init__()
        self.latent_dim = latent_dim
        self.image_size = image_size
        
        # Decoder architecture
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 256 * 8 * 8),
            nn.ReLU(),
            nn.Unflatten(1, (256, 8, 8)),
            
            nn.ConvTranspose2d(256, 128, 4, stride=2, padding=1),  # 16x16
            nn.BatchNorm2d(128),
            nn.ReLU(),
            
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1),   # 32x32
            nn.BatchNorm2d(64),
            nn.ReLU(),
            
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),    # 64x64
            nn.BatchNorm2d(32),
            nn.ReLU(),
            
            nn.ConvTranspose2d(32, 16, 4, stride=2, padding=1),    # 128x128
            nn.BatchNorm2d(16),
            nn.ReLU(),
            
            nn.ConvTranspose2d(16, 8, 4, stride=2, padding=1),     # 256x256
            nn.BatchNorm2d(8),
            nn.ReLU(),
            
            nn.ConvTranspose2d(8, 3, 4, stride=2, padding=1),      # 512x512
            nn.Tanh()
        )
        
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent vector to image"""
        return self.decoder(z)
    
    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.decode(z)


class VectorImageGenerator:
    """Main class for generating images from vectors"""
    
    def __init__(self):
        self.vae = SimpleVAE(LATENT_DIM, IMAGE_SIZE).to(DEVICE)
        self.vae.eval()  # Set to evaluation mode
        
        # Initialize with random weights (in production, load pre-trained weights)
        self._initialize_weights()
        
    def _initialize_weights(self):
        """Initialize model weights"""
        for m in self.vae.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    async def generate_from_vector(
        self,
        vector: List[float],
        size: int = 512,
        method: str = "vae",
        strength: float = 1.0,
        seed: Optional[int] = None
    ) -> Image.Image:
        """Generate image from vector embedding"""
        
        # Set random seed if provided
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
        
        # Convert to tensor and normalize
        z = torch.tensor(vector, dtype=torch.float32).to(DEVICE)
        z = z.view(1, -1)  # Add batch dimension
        
        # Normalize vector
        z = z / (torch.norm(z, dim=1, keepdim=True) + 1e-8)
        z = z * strength
        
        if method == "vae":
            image = await self._generate_vae(z, size)
        elif method == "diffusion":
            image = await self._generate_diffusion(z, size)
        elif method == "gan":
            image = await self._generate_gan(z, size)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return image
    
    async def _generate_vae(self, z: torch.Tensor, size: int) -> Image.Image:
        """Generate using VAE decoder"""
        with torch.no_grad():
            # Generate image
            generated = self.vae.decode(z)
            
            # Convert to PIL image
            generated = (generated + 1) / 2  # From [-1, 1] to [0, 1]
            generated = generated.clamp(0, 1)
            generated = generated.cpu().squeeze(0).permute(1, 2, 0)
            generated = (generated.numpy() * 255).astype(np.uint8)
            
            image = Image.fromarray(generated)
            
            # Resize if needed
            if size != IMAGE_SIZE:
                image = image.resize((size, size), Image.Resampling.LANCZOS)
            
            return image
    
    async def _generate_diffusion(self, z: torch.Tensor, size: int) -> Image.Image:
        """Generate using diffusion-based method (simplified)"""
        # This is a placeholder - in production, use a proper diffusion model
        # For now, we'll use a modified VAE approach with noise
        
        with torch.no_grad():
            # Add controlled noise for diffusion-like effect
            noise_steps = 10
            image_tensor = torch.zeros(1, 3, size, size).to(DEVICE)
            
            for t in range(noise_steps):
                alpha = 1 - (t / noise_steps)
                noise = torch.randn_like(image_tensor) * alpha * 0.1
                
                # Use VAE decoder with modified input
                z_noisy = z + torch.randn_like(z) * alpha * 0.05
                decoded = self.vae.decode(z_noisy)
                
                # Blend with previous
                image_tensor = alpha * decoded + (1 - alpha) * image_tensor + noise
            
            # Convert to PIL
            image_tensor = (image_tensor + 1) / 2
            image_tensor = image_tensor.clamp(0, 1)
            image_tensor = image_tensor.cpu().squeeze(0).permute(1, 2, 0)
            image_array = (image_tensor.numpy() * 255).astype(np.uint8)
            
            return Image.fromarray(image_array)
    
    async def _generate_gan(self, z: torch.Tensor, size: int) -> Image.Image:
        """Generate using GAN-style approach"""
        # Placeholder - in production, use a proper GAN generator
        # For now, use VAE with style modifications
        
        with torch.no_grad():
            # Apply style transformations
            z_styled = z.clone()
            
            # Add style-specific modifications
            style_vector = torch.randn(1, 64).to(DEVICE) * 0.1
            z_styled[:, :64] += style_vector
            
            # Generate with modified vector
            image = await self._generate_vae(z_styled, size)
            
            # Apply post-processing for GAN-like sharpness
            image_array = np.array(image)
            from scipy.ndimage import gaussian_filter
            
            # Unsharp mask for enhancement
            blurred = gaussian_filter(image_array, sigma=1.0)
            sharpened = image_array + 0.5 * (image_array - blurred)
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
            
            return Image.fromarray(sharpened)
    
    def interpolate_vectors(
        self,
        vector1: List[float],
        vector2: List[float],
        steps: int = 10
    ) -> List[List[float]]:
        """Interpolate between two vectors"""
        v1 = np.array(vector1)
        v2 = np.array(vector2)
        
        # Spherical interpolation for better results
        interpolated = []
        for i in range(steps):
            t = i / (steps - 1)
            
            # Normalize vectors
            v1_norm = v1 / (np.linalg.norm(v1) + 1e-8)
            v2_norm = v2 / (np.linalg.norm(v2) + 1e-8)
            
            # Spherical interpolation
            omega = np.arccos(np.clip(np.dot(v1_norm, v2_norm), -1, 1))
            if omega < 1e-6:
                # Vectors are too similar, use linear interpolation
                v_interp = (1 - t) * v1 + t * v2
            else:
                v_interp = (np.sin((1 - t) * omega) / np.sin(omega)) * v1 + \
                          (np.sin(t * omega) / np.sin(omega)) * v2
            
            interpolated.append(v_interp.tolist())
        
        return interpolated
    
    def modify_vector(
        self,
        vector: List[float],
        modifications: Dict[str, float]
    ) -> List[float]:
        """Modify vector based on semantic attributes"""
        v = np.array(vector)
        
        # Define attribute mappings (simplified)
        attribute_indices = {
            "brightness": range(0, 64),
            "color_warmth": range(64, 128),
            "detail": range(128, 192),
            "style": range(192, 256),
            "composition": range(256, 320),
            "texture": range(320, 384),
            "mood": range(384, 448),
            "contrast": range(448, 512)
        }
        
        # Apply modifications
        for attr, value in modifications.items():
            if attr in attribute_indices:
                indices = attribute_indices[attr]
                # Modify relevant dimensions
                v[list(indices)] += value * 0.1  # Scale factor
        
        # Renormalize
        v = v / (np.linalg.norm(v) + 1e-8)
        
        return v.tolist()


# Initialize FastAPI app
app = FastAPI(
    title="Vector to Image Generation Server",
    description="Generate images directly from vector embeddings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize generator
generator = VectorImageGenerator()


@app.post("/generate", response_model=ImageResponse)
async def generate_image(request: VectorRequest):
    """Generate image from vector embedding"""
    try:
        # Validate vector dimensions
        if len(request.vector) != LATENT_DIM:
            raise HTTPException(
                status_code=400,
                detail=f"Vector must have {LATENT_DIM} dimensions, got {len(request.vector)}"
            )
        
        # Generate image
        image = await generator.generate_from_vector(
            vector=request.vector,
            size=request.size,
            method=request.method,
            strength=request.strength,
            seed=request.seed
        )
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return ImageResponse(
            image=f"data:image/png;base64,{image_base64}",
            method=request.method,
            metadata={
                "size": request.size,
                "strength": request.strength,
                "seed": request.seed,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interpolate")
async def interpolate_vectors(
    vector1: List[float],
    vector2: List[float],
    steps: int = 10
):
    """Interpolate between two vectors"""
    try:
        if len(vector1) != LATENT_DIM or len(vector2) != LATENT_DIM:
            raise HTTPException(
                status_code=400,
                detail=f"Vectors must have {LATENT_DIM} dimensions"
            )
        
        interpolated = generator.interpolate_vectors(vector1, vector2, steps)
        
        return {
            "interpolated_vectors": interpolated,
            "steps": steps
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/modify")
async def modify_vector(
    vector: List[float],
    modifications: Dict[str, float]
):
    """Modify vector based on semantic attributes"""
    try:
        if len(vector) != LATENT_DIM:
            raise HTTPException(
                status_code=400,
                detail=f"Vector must have {LATENT_DIM} dimensions"
            )
        
        modified = generator.modify_vector(vector, modifications)
        
        return {
            "modified_vector": modified,
            "modifications": modifications
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch_generate")
async def batch_generate(
    vectors: List[List[float]],
    size: int = 512,
    method: str = "vae"
):
    """Generate multiple images from vectors"""
    try:
        images = []
        
        for i, vector in enumerate(vectors):
            if len(vector) != LATENT_DIM:
                raise HTTPException(
                    status_code=400,
                    detail=f"Vector {i} must have {LATENT_DIM} dimensions"
                )
            
            # Generate image
            image = await generator.generate_from_vector(
                vector=vector,
                size=size,
                method=method
            )
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            images.append({
                "index": i,
                "image": f"data:image/png;base64,{image_base64}"
            })
        
        return {
            "images": images,
            "count": len(images),
            "method": method
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "device": str(DEVICE),
        "latent_dim": LATENT_DIM,
        "image_size": IMAGE_SIZE
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Vector to Image Generation Server",
        "endpoints": [
            "/generate - Generate single image from vector",
            "/interpolate - Interpolate between vectors",
            "/modify - Modify vector attributes",
            "/batch_generate - Generate multiple images",
            "/health - Health check"
        ],
        "vector_dimension": LATENT_DIM,
        "supported_methods": ["vae", "diffusion", "gan"]
    }


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8888,
        log_level="info"
    )