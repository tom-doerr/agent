#!/usr/bin/env python3
"""
Example client for the Vector Image Generation Server

This demonstrates how to:
1. Generate images from vectors
2. Interpolate between vectors
3. Modify vectors semantically
4. Batch generate multiple images
"""

import requests
import numpy as np
import base64
from PIL import Image
import io
from typing import List, Dict


class VectorImageClient:
    """Client for interacting with the vector image server"""
    
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url
        
    def generate_random_vector(self, dim: int = 512) -> List[float]:
        """Generate a random normalized vector"""
        vector = np.random.randn(dim)
        vector = vector / np.linalg.norm(vector)
        return vector.tolist()
    
    def generate_image(
        self,
        vector: List[float],
        size: int = 512,
        method: str = "vae",
        strength: float = 1.0,
        seed: int = None
    ) -> Image.Image:
        """Generate an image from a vector"""
        
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "vector": vector,
                "size": size,
                "method": method,
                "strength": strength,
                "seed": seed
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extract base64 image
            image_data = data["image"].split(",")[1]
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            return image
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    
    def interpolate_vectors(
        self,
        vector1: List[float],
        vector2: List[float],
        steps: int = 10
    ) -> List[List[float]]:
        """Interpolate between two vectors"""
        
        response = requests.post(
            f"{self.base_url}/interpolate",
            json={
                "vector1": vector1,
                "vector2": vector2,
                "steps": steps
            }
        )
        
        if response.status_code == 200:
            return response.json()["interpolated_vectors"]
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    
    def modify_vector(
        self,
        vector: List[float],
        modifications: Dict[str, float]
    ) -> List[float]:
        """Modify a vector based on semantic attributes"""
        
        response = requests.post(
            f"{self.base_url}/modify",
            json={
                "vector": vector,
                "modifications": modifications
            }
        )
        
        if response.status_code == 200:
            return response.json()["modified_vector"]
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    
    def batch_generate(
        self,
        vectors: List[List[float]],
        size: int = 512,
        method: str = "vae"
    ) -> List[Image.Image]:
        """Generate multiple images from vectors"""
        
        response = requests.post(
            f"{self.base_url}/batch_generate",
            json={
                "vectors": vectors,
                "size": size,
                "method": method
            }
        )
        
        if response.status_code == 200:
            images = []
            for img_data in response.json()["images"]:
                # Extract base64 image
                image_data = img_data["image"].split(",")[1]
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                images.append(image)
            return images
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")


def main():
    """Example usage of the vector image client"""
    
    # Initialize client
    client = VectorImageClient()
    
    print("Vector Image Generation Examples")
    print("=" * 50)
    
    # Example 1: Generate a single image
    print("\n1. Generating single image from random vector...")
    vector = client.generate_random_vector()
    image = client.generate_image(vector, size=512, method="vae")
    image.save("example_single.png")
    print("   ✓ Saved as example_single.png")
    
    # Example 2: Generate with different methods
    print("\n2. Generating with different methods...")
    methods = ["vae", "diffusion", "gan"]
    for method in methods:
        image = client.generate_image(vector, size=256, method=method)
        image.save(f"example_{method}.png")
        print(f"   ✓ Saved as example_{method}.png")
    
    # Example 3: Vector interpolation
    print("\n3. Interpolating between two vectors...")
    vector1 = client.generate_random_vector()
    vector2 = client.generate_random_vector()
    
    interpolated = client.interpolate_vectors(vector1, vector2, steps=5)
    
    for i, vec in enumerate(interpolated):
        image = client.generate_image(vec, size=256)
        image.save(f"example_interpolation_{i}.png")
    print(f"   ✓ Saved {len(interpolated)} interpolation frames")
    
    # Example 4: Semantic modifications
    print("\n4. Modifying vector semantically...")
    base_vector = client.generate_random_vector()
    
    modifications = {
        "brightness": 0.5,
        "color_warmth": -0.3,
        "detail": 0.7,
        "style": 0.2
    }
    
    modified_vector = client.modify_vector(base_vector, modifications)
    
    # Generate before and after
    image_before = client.generate_image(base_vector, size=256)
    image_after = client.generate_image(modified_vector, size=256)
    
    image_before.save("example_before_modification.png")
    image_after.save("example_after_modification.png")
    print("   ✓ Saved before/after modification examples")
    
    # Example 5: Batch generation
    print("\n5. Batch generating multiple images...")
    vectors = [client.generate_random_vector() for _ in range(4)]
    images = client.batch_generate(vectors, size=256)
    
    for i, img in enumerate(images):
        img.save(f"example_batch_{i}.png")
    print(f"   ✓ Generated {len(images)} images in batch")
    
    # Example 6: Creating a style matrix
    print("\n6. Creating style variation matrix...")
    base_vector = client.generate_random_vector()
    
    # Create variations
    attributes = ["brightness", "color_warmth", "detail", "contrast"]
    values = [-0.5, 0, 0.5]
    
    grid_images = []
    for attr in attributes:
        row_images = []
        for val in values:
            mod_vector = client.modify_vector(base_vector, {attr: val})
            img = client.generate_image(mod_vector, size=128)
            row_images.append(img)
        grid_images.append(row_images)
    
    # Create grid image
    grid_width = len(values) * 128
    grid_height = len(attributes) * 128
    grid = Image.new('RGB', (grid_width, grid_height))
    
    for i, row in enumerate(grid_images):
        for j, img in enumerate(row):
            grid.paste(img, (j * 128, i * 128))
    
    grid.save("example_style_matrix.png")
    print("   ✓ Saved style variation matrix")
    
    print("\n✅ All examples completed successfully!")
    print("   Generated images saved in current directory")


if __name__ == "__main__":
    main()