#!/usr/bin/env python
"""End-to-end API tests for the AI Art Generator"""

import httpx
import asyncio
import time
import sys

BASE_URL = "http://backend:8090"

async def test_health():
    """Test the health endpoint"""
    print("1. Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("   ✓ Health check passed")

async def test_generate_image():
    """Test image generation"""
    print("\n2. Testing image generation...")
    async with httpx.AsyncClient() as client:
        # Start generation
        response = await client.post(
            f"{BASE_URL}/generate",
            json={
                "prompt": "A futuristic city at sunset",
                "provider": "openai",
                "size": "512x512"
            }
        )
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        assert data["status"] == "pending"
        print(f"   ✓ Generation started (task_id: {task_id})")
        
        # Wait for completion
        max_attempts = 30
        for i in range(max_attempts):
            response = await client.get(f"{BASE_URL}/status/{task_id}")
            status_data = response.json()
            
            if status_data["status"] == "completed":
                print("   ✓ Image generated successfully")
                return status_data["result"]
            elif status_data["status"] == "failed":
                print(f"   ✗ Generation failed: {status_data.get('error')}")
                assert False, "Image generation failed"
            
            await asyncio.sleep(1)
        
        assert False, "Image generation timed out"

async def test_list_images():
    """Test listing images"""
    print("\n3. Testing image listing...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/images")
        assert response.status_code == 200
        images = response.json()
        print(f"   ✓ Found {len(images)} images")
        return images

async def test_preference_comparison(image1_id, image2_id):
    """Test preference comparison"""
    print("\n4. Testing preference comparison...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/preferences/compare",
            json={
                "winner_id": image1_id,
                "loser_id": image2_id,
                "comparison_type": "a_b_test"
            }
        )
        assert response.status_code == 200
        print("   ✓ Preference comparison recorded")

async def test_preference_rating(image_id):
    """Test preference rating"""
    print("\n5. Testing preference rating...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/preferences/rate",
            json={
                "image_id": image_id,
                "score": 0.8,
                "feedback_type": "rating"
            }
        )
        assert response.status_code == 200
        print("   ✓ Preference rating recorded")

async def test_preference_prediction(image_id):
    """Test preference prediction"""
    print("\n6. Testing preference prediction...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/predict/{image_id}")
        assert response.status_code == 200
        data = response.json()
        assert "predicted_score" in data
        assert "confidence" in data
        print(f"   ✓ Prediction: score={data['predicted_score']:.2f}, confidence={data['confidence']:.2f}")

async def test_suggest_comparison():
    """Test comparison suggestion"""
    print("\n7. Testing comparison suggestion...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/preferences/suggest-comparison")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Suggested comparison: {data['image1_id'][:8]}... vs {data['image2_id'][:8]}...")
        else:
            print("   ⚠ Not enough images for comparison suggestion")

async def main():
    """Run all E2E tests"""
    print("=" * 60)
    print("AI Art Generator E2E Tests")
    print("=" * 60)
    
    try:
        # Basic tests
        await test_health()
        
        # Generate images
        print("\nGenerating test images...")
        image1 = await test_generate_image()
        
        # Generate second image with different prompt
        print("\nGenerating second test image...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/generate",
                json={
                    "prompt": "Abstract geometric patterns",
                    "provider": "local",  # Try local provider
                    "size": "512x512"
                }
            )
            task_id = response.json()["task_id"]
            # Wait briefly
            await asyncio.sleep(2)
            response = await client.get(f"{BASE_URL}/status/{task_id}")
            image2 = response.json().get("result")
        
        # List images
        images = await test_list_images()
        
        if len(images) >= 2:
            # Test preferences with generated images
            await test_preference_comparison(images[0]["id"], images[1]["id"])
            await test_preference_rating(images[0]["id"])
            await test_preference_prediction(images[0]["id"])
            await test_suggest_comparison()
        else:
            print("\n⚠ Not enough images for preference tests")
        
        print("\n" + "=" * 60)
        print("✅ All E2E tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())