#!/usr/bin/env python
import httpx
import json
import sys
import asyncio

async def test_health():
    print("Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8090/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        print("✓ Health check passed\n")

async def test_generate():
    print("Testing image generation...")
    data = {
        "prompt": "A beautiful sunset over mountains",
        "provider": "openai",
        "size": "512x512"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8090/generate", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Task ID: {result.get('task_id')}")
        print(f"Status: {result.get('status')}")
        assert response.status_code == 200
        print("✓ Generation started\n")
        return result.get('task_id')

async def test_get_images():
    print("Testing get images...")
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8090/images")
        print(f"Status: {response.status_code}")
        images = response.json()
        print(f"Number of images: {len(images)}")
        assert response.status_code == 200
        print("✓ Get images passed\n")

async def main():
    try:
        await test_health()
        task_id = await test_generate()
        await test_get_images()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())