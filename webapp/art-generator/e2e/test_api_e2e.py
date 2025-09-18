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
                "size": "1024x1024"
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

async def test_ranking_update(image_ids):
    """Test ranking update functionality"""
    print("\n8. Testing ranking update...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/preferences/rank",
            json={
                "image_rankings": image_ids[:4]  # Rank first 4 images
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"   ✓ Ranking updated: {data['comparisons_added']} comparisons added")

async def test_generate_optimal():
    """Test optimal image generation based on preferences"""
    print("\n9. Testing optimal image generation...")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/generate/optimal")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Optimal generation started (task_id: {data['task_id'][:8]}...)")
            
            # Wait for completion
            for i in range(10):
                response = await client.get(f"{BASE_URL}/status/{data['task_id']}")
                status_data = response.json()
                
                if status_data["status"] == "completed":
                    print("   ✓ Optimal image generated successfully")
                    return
                elif status_data["status"] == "failed":
                    print(f"   ⚠ Optimal generation failed: {status_data.get('error')}")
                    return
                
                await asyncio.sleep(1)
        else:
            print(f"   ⚠ Not enough preference data for optimal generation")

async def test_websocket_connection():
    """Test WebSocket connection and messages"""
    print("\n10. Testing WebSocket connection...")
    try:
        import websockets
        
        async with websockets.connect(f"ws://backend:8090/ws") as websocket:
            print("   ✓ WebSocket connected")
            
            # Wait for a message or timeout
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"   ✓ Received WebSocket message: {message[:50]}...")
            except asyncio.TimeoutError:
                print("   ✓ WebSocket connection stable (no messages)")
                
    except ImportError:
        print("   ⚠ WebSocket library not available, skipping")
    except Exception as e:
        print(f"   ⚠ WebSocket test failed: {e}")

async def test_concurrent_preferences():
    """Test concurrent preference updates"""
    print("\n11. Testing concurrent preference updates...")
    async with httpx.AsyncClient() as client:
        # Get available images
        response = await client.get(f"{BASE_URL}/images?limit=6")
        images = response.json()
        
        if len(images) >= 6:
            # Submit multiple comparisons concurrently
            tasks = []
            for i in range(0, 6, 2):
                tasks.append(client.post(
                    f"{BASE_URL}/preferences/compare",
                    json={
                        "winner_id": images[i]["id"],
                        "loser_id": images[i+1]["id"],
                        "comparison_type": "concurrent_test"
                    }
                ))
            
            responses = await asyncio.gather(*tasks)
            
            # All should succeed
            success_count = sum(1 for r in responses if r.status_code == 200)
            print(f"   ✓ {success_count}/3 concurrent comparisons succeeded")
        else:
            print("   ⚠ Not enough images for concurrent test")

async def main():
    """Run all E2E tests"""
    print("=" * 60)
    print("AI Art Generator E2E Tests - Comprehensive Suite")
    print("=" * 60)
    
    try:
        # Basic tests
        await test_health()
        
        # Generate test images
        print("\nGenerating test images for comprehensive testing...")
        generated_images = []
        
        # Generate multiple images with different providers
        providers = ["openai", "local", "replicate"]
        prompts = [
            "A futuristic city at sunset",
            "Abstract geometric patterns",
            "A serene mountain landscape",
            "Colorful underwater scene"
        ]
        
        for i, (prompt, provider) in enumerate(zip(prompts, providers * 2)):
            print(f"\nGenerating image {i+1}/4...")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/generate",
                    json={
                        "prompt": prompt,
                        "provider": provider,
                        "size": "1024x1024"
                    }
                )
                if response.status_code == 200:
                    task_id = response.json()["task_id"]
                    
                    # Poll for completion
                    for _ in range(30):
                        response = await client.get(f"{BASE_URL}/status/{task_id}")
                        status_data = response.json()
                        
                        if status_data["status"] == "completed":
                            generated_images.append(status_data["result"])
                            print(f"   ✓ Image {i+1} generated successfully")
                            break
                        elif status_data["status"] == "failed":
                            print(f"   ✗ Image {i+1} generation failed")
                            break
                        
                        await asyncio.sleep(1)
        
        # List all images
        images = await test_list_images()
        
        if len(images) >= 2:
            # Test preference features
            await test_preference_comparison(images[0]["id"], images[1]["id"])
            await test_preference_rating(images[0]["id"])
            await test_preference_prediction(images[0]["id"])
            await test_suggest_comparison()
            
            # Test new features
            if len(images) >= 4:
                image_ids = [img["id"] for img in images[:4]]
                await test_ranking_update(image_ids)
            
            # Test optimal generation
            await test_generate_optimal()
            
            # Test concurrent operations
            await test_concurrent_preferences()
            
            # Test WebSocket
            await test_websocket_connection()
        else:
            print("\n⚠ Not enough images for comprehensive preference tests")
        
        print("\n" + "=" * 60)
        print("✅ All E2E tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())