import os
import asyncio
import hashlib
import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime
import openai
import replicate
from models import ImageProvider, GeneratedImage
import httpx
import base64
from PIL import Image, ImageDraw, ImageFont
import io


class ImageGenerator:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        self.local_model_url = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434")  # Ollama default
        self.local_model_name = os.getenv("LOCAL_MODEL_NAME", "stable-diffusion")
        
        # Check if local model is available
        self.local_available = self._check_local_model()
        
        self.mock_mode = not (self.openai_key or self.replicate_token or self.local_available)
        
        if self.openai_key:
            self.openai_client = openai.AsyncOpenAI(api_key=self.openai_key)
        else:
            self.openai_client = None
        
    def _check_local_model(self) -> bool:
        """Check if local model is available."""
        try:
            import requests
            response = requests.get(f"{self.local_model_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    async def generate_image(
        self,
        prompt: str,
        provider: ImageProvider,
        negative_prompt: Optional[str] = None,
        size: str = "1024x1024",
        style: Optional[str] = None,
        latent_vector: Optional[List[float]] = None,
        **kwargs
    ) -> GeneratedImage:
        """Generate an image using the specified provider."""
        
        if self.mock_mode and provider != ImageProvider.LOCAL:
            return await self._generate_mock(prompt, size, style, latent_vector)
        
        if provider == ImageProvider.OPENAI:
            return await self._generate_openai(prompt, size, style, latent_vector)
        elif provider == ImageProvider.REPLICATE:
            return await self._generate_replicate(prompt, negative_prompt, size, style, latent_vector)
        elif provider == ImageProvider.LOCAL:
            return await self._generate_local(prompt, negative_prompt, size, style, latent_vector)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _generate_openai(
        self,
        prompt: str,
        size: str,
        style: Optional[str] = None,
        latent_vector: Optional[List[float]] = None
    ) -> GeneratedImage:
        """Generate image using OpenAI DALL-E 3."""
        
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
        
        response = await self.openai_client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size=size,
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        image_id = hashlib.md5(f"{prompt}{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        # Use provided latent vector or generate a new one
        if latent_vector is None:
            latent_vector = self._generate_latent_vector(prompt)
        else:
            # Modify prompt based on latent vector characteristics
            full_prompt = self._modify_prompt_from_latent(full_prompt, latent_vector)
        
        return GeneratedImage(
            id=image_id,
            url=image_url,
            prompt=prompt,
            provider=ImageProvider.OPENAI,
            latent_vector=latent_vector,
            created_at=datetime.utcnow(),
            metadata={"style": style, "size": size}
        )
    
    async def _generate_replicate(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        size: str,
        style: Optional[str] = None,
        latent_vector: Optional[List[float]] = None
    ) -> GeneratedImage:
        """Generate image using Replicate (Stable Diffusion)."""
        
        width, height = map(int, size.split('x'))
        
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
            
        # Apply latent vector modifications if provided
        if latent_vector is not None:
            full_prompt = self._modify_prompt_from_latent(full_prompt, latent_vector)
        
        # Using SDXL model
        model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        
        async with httpx.AsyncClient() as client:
            # Start the prediction
            response = await client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Token {self.replicate_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": model.split(":")[-1],
                    "input": {
                        "prompt": full_prompt,
                        "negative_prompt": negative_prompt or "",
                        "width": width,
                        "height": height,
                        "num_outputs": 1
                    }
                }
            )
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for completion
            while True:
                response = await client.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers={"Authorization": f"Token {self.replicate_token}"}
                )
                
                prediction = response.json()
                
                if prediction["status"] == "succeeded":
                    image_url = prediction["output"][0]
                    break
                elif prediction["status"] == "failed":
                    raise Exception(f"Replicate generation failed: {prediction.get('error')}")
                
                await asyncio.sleep(1)
        
        image_id = hashlib.md5(f"{prompt}{datetime.utcnow().isoformat()}".encode()).hexdigest()
        if latent_vector is None:
            latent_vector = self._generate_latent_vector(prompt)
        
        return GeneratedImage(
            id=image_id,
            url=image_url,
            prompt=prompt,
            provider=ImageProvider.REPLICATE,
            latent_vector=latent_vector,
            created_at=datetime.utcnow(),
            metadata={
                "style": style,
                "size": size,
                "negative_prompt": negative_prompt
            }
        )
    
    def _generate_latent_vector(self, prompt: str, dim: int = 512) -> List[float]:
        """Generate a mock latent vector for the image.
        
        In a real implementation, this would use a vision model like CLIP
        to generate actual image embeddings.
        """
        # Use prompt hash as seed for reproducibility
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        np.random.seed(seed)
        
        # Generate normalized random vector
        vector = np.random.randn(dim)
        vector = vector / np.linalg.norm(vector)
        
        return vector.tolist()
    
    def _modify_prompt_from_latent(self, prompt: str, latent_vector: List[float]) -> str:
        """Modify prompt based on latent vector characteristics.
        
        This analyzes the latent vector to extract style preferences
        and modifies the prompt accordingly.
        """
        # Extract features from latent vector
        vector_np = np.array(latent_vector[:64])  # Use first 64 dimensions
        
        # Analyze vector for style characteristics
        brightness = np.mean(vector_np[:16])
        color_warmth = np.mean(vector_np[16:32])
        detail_level = np.mean(vector_np[32:48])
        artistic_style = np.mean(vector_np[48:64])
        
        modifiers = []
        
        # Add modifiers based on latent characteristics
        if brightness > 0.5:
            modifiers.append("bright, vibrant")
        elif brightness < -0.5:
            modifiers.append("dark, moody")
            
        if color_warmth > 0.5:
            modifiers.append("warm colors")
        elif color_warmth < -0.5:
            modifiers.append("cool colors")
            
        if detail_level > 0.5:
            modifiers.append("highly detailed, intricate")
        elif detail_level < -0.5:
            modifiers.append("minimalist, simple")
            
        if artistic_style > 0.5:
            modifiers.append("artistic, painterly")
        elif artistic_style < -0.5:
            modifiers.append("photorealistic, sharp")
        
        # Combine prompt with modifiers
        if modifiers:
            return f"{prompt}, {', '.join(modifiers)}"
        return prompt
    
    async def _generate_mock(
        self,
        prompt: str,
        size: str,
        style: Optional[str] = None,
        latent_vector: Optional[List[float]] = None
    ) -> GeneratedImage:
        """Generate a mock image for local development without API keys."""
        
        # Parse size
        width, height = map(int, size.split('x'))
        
        # Create a colorful gradient image based on prompt hash or latent vector
        if latent_vector is not None:
            # Use latent vector to influence colors
            seed = int(np.sum(np.array(latent_vector[:8]) * 1000000))
        else:
            seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        np.random.seed(seed)
        
        # Create image with gradient
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Generate colors based on prompt
        colors = [
            tuple(np.random.randint(0, 256, 3)),
            tuple(np.random.randint(0, 256, 3)),
            tuple(np.random.randint(0, 256, 3))
        ]
        
        # Draw gradient
        for i in range(height):
            r = int(colors[0][0] * (1 - i/height) + colors[1][0] * (i/height))
            g = int(colors[0][1] * (1 - i/height) + colors[1][1] * (i/height))
            b = int(colors[0][2] * (1 - i/height) + colors[1][2] * (i/height))
            draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))
        
        # Add text overlay
        text = f"{prompt[:50]}..."
        if style:
            text += f"\n[{style}]"
        
        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Add text with background
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw background rectangle
        padding = 20
        draw.rectangle(
            [(x - padding, y - padding), (x + text_width + padding, y + text_height + padding)],
            fill=(0, 0, 0, 128)
        )
        
        # Draw text
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Convert to base64 data URL
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        base64_image = base64.b64encode(buffer.getvalue()).decode()
        data_url = f"data:image/png;base64,{base64_image}"
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        image_id = hashlib.md5(f"{prompt}{datetime.utcnow().isoformat()}".encode()).hexdigest()
        if latent_vector is None:
            latent_vector = self._generate_latent_vector(prompt)
        
        return GeneratedImage(
            id=image_id,
            url=data_url,
            prompt=prompt,
            provider=ImageProvider.OPENAI,  # Default to OpenAI for mock
            latent_vector=latent_vector,
            created_at=datetime.utcnow(),
            metadata={"style": style, "size": size, "mock": True}
        )
    
    async def _generate_local(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        size: str,
        style: Optional[str] = None,
        latent_vector: Optional[List[float]] = None
    ) -> GeneratedImage:
        """Generate image using local model (Ollama, LocalAI, or ComfyUI)."""
        
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
            
        # Apply latent vector modifications if provided
        if latent_vector is not None:
            full_prompt = self._modify_prompt_from_latent(full_prompt, latent_vector)
        
        # For Ollama with LLaVA or similar multimodal models
        # This is a simplified implementation - adapt based on your local setup
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                # Try Stable Diffusion WebUI API format
                response = await client.post(
                    f"{self.local_model_url}/sdapi/v1/txt2img",
                    json={
                        "prompt": full_prompt,
                        "negative_prompt": negative_prompt or "",
                        "width": int(size.split('x')[0]),
                        "height": int(size.split('x')[1]),
                        "steps": 20,
                        "cfg_scale": 7.5,
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_data = result.get("images", [None])[0]
                    if image_data:
                        image_url = f"data:image/png;base64,{image_data}"
                    else:
                        # Fallback to mock if no image returned
                        return await self._generate_mock(prompt, size, style)
                else:
                    # If SD WebUI not available, try ComfyUI or fallback to mock
                    return await self._generate_mock(prompt, size, style)
                    
            except Exception as e:
                print(f"Local generation failed: {e}")
                # Fallback to mock mode
                return await self._generate_mock(prompt, size, style)
        
        image_id = hashlib.md5(f"{prompt}{datetime.utcnow().isoformat()}".encode()).hexdigest()
        if latent_vector is None:
            latent_vector = self._generate_latent_vector(prompt)
        
        return GeneratedImage(
            id=image_id,
            url=image_url,
            prompt=prompt,
            provider=ImageProvider.LOCAL,
            latent_vector=latent_vector,
            created_at=datetime.utcnow(),
            metadata={
                "style": style,
                "size": size,
                "negative_prompt": negative_prompt,
                "local_model": self.local_model_name
            }
        )
    
    async def get_image_embedding(self, image_url: str) -> List[float]:
        """Get embedding for an existing image.
        
        In production, this would download the image and run it through
        a vision model to get the actual embedding.
        """
        # For now, return a mock embedding
        seed = int(hashlib.md5(image_url.encode()).hexdigest()[:8], 16)
        np.random.seed(seed)
        vector = np.random.randn(512)
        vector = vector / np.linalg.norm(vector)
        return vector.tolist()