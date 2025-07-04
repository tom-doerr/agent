#!/usr/bin/env python3
"""
Stress test for concurrent streaming
"""
import asyncio
import httpx
import time
import statistics
import sys

async def test_stream(session: httpx.AsyncClient, question: str, model: str = "gemini-flash") -> dict:
    """Test a single streaming request"""
    start_time = time.time()
    chunks = 0
    tokens = 0
    error = None
    
    try:
        async with session.stream('GET', f"http://localhost:8000/stream/{question}?model={model}") as response:
            if response.status_code != 200:
                error = f"HTTP {response.status_code}"
                return {"error": error, "duration": 0}
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunks += 1
                    try:
                        import json
                        data = json.loads(line[6:])
                        if "total_tokens" in data:
                            tokens = data["total_tokens"]
                    except:
                        pass
                        
    except Exception as e:
        error = str(e)
    
    duration = time.time() - start_time
    return {
        "chunks": chunks,
        "tokens": tokens,
        "duration": duration,
        "error": error
    }

async def run_concurrent_tests(n_requests: int = 10, model: str = "mock"):
    """Run n concurrent streaming requests"""
    print(f"\n🚀 Running {n_requests} concurrent requests with model: {model}")
    
    async with httpx.AsyncClient(timeout=30.0) as session:
        # Create tasks
        tasks = []
        for i in range(n_requests):
            question = f"Question{i}: What is the meaning of life?"
            tasks.append(test_stream(session, question, model))
        
        # Run concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
    
    # Analyze results
    successful = [r for r in results if isinstance(r, dict) and not r.get("error")]
    failed = [r for r in results if not isinstance(r, dict) or r.get("error")]
    
    print(f"\n📊 Results:")
    print(f"Total time: {total_time:.2f}s")
    print(f"Successful: {len(successful)}/{n_requests}")
    print(f"Failed: {len(failed)}/{n_requests}")
    
    if successful:
        durations = [r["duration"] for r in successful]
        chunks = [r["chunks"] for r in successful]
        tokens = [r["tokens"] for r in successful if r["tokens"] > 0]
        
        print(f"\n⏱️  Response times:")
        print(f"  Min: {min(durations):.2f}s")
        print(f"  Max: {max(durations):.2f}s")
        print(f"  Avg: {statistics.mean(durations):.2f}s")
        print(f"  P95: {statistics.quantiles(durations, n=20)[18]:.2f}s")
        
        print(f"\n📦 Chunks per request:")
        print(f"  Avg: {statistics.mean(chunks):.1f}")
        
        if tokens:
            print(f"\n🔤 Tokens per request:")
            print(f"  Avg: {statistics.mean(tokens):.1f}")
    
    if failed:
        print(f"\n❌ Errors:")
        for i, result in enumerate(results):
            if not isinstance(result, dict):
                print(f"  Request {i}: Exception - {result}")
            elif result.get("error"):
                print(f"  Request {i}: {result['error']}")

async def run_sustained_load(duration_seconds: int = 30, rps: float = 5.0, model: str = "mock"):
    """Run sustained load test"""
    print(f"\n🏃 Running sustained load test")
    print(f"Duration: {duration_seconds}s, Target RPS: {rps}, Model: {model}")
    
    interval = 1.0 / rps
    start_time = time.time()
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as session:
        request_id = 0
        
        while time.time() - start_time < duration_seconds:
            # Launch request
            question = f"Load test {request_id}: Explain quantum computing"
            task = asyncio.create_task(test_stream(session, question, model))
            results.append(task)
            request_id += 1
            
            # Wait for next request slot
            await asyncio.sleep(interval)
        
        # Wait for all requests to complete
        print(f"\n⏳ Waiting for {len(results)} requests to complete...")
        all_results = await asyncio.gather(*results, return_exceptions=True)
    
    # Analyze
    successful = [r for r in all_results if isinstance(r, dict) and not r.get("error")]
    failed = len(all_results) - len(successful)
    
    print(f"\n📊 Sustained load results:")
    print(f"Total requests: {len(all_results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(all_results)*100:.1f}%)")
    print(f"Failed: {failed}")
    print(f"Actual RPS: {len(all_results)/duration_seconds:.2f}")
    
    if successful:
        durations = [r["duration"] for r in successful]
        print(f"\nResponse times under load:")
        print(f"  Avg: {statistics.mean(durations):.2f}s")
        print(f"  P95: {statistics.quantiles(durations, n=20)[18]:.2f}s")

async def main():
    """Run stress tests"""
    model = sys.argv[1] if len(sys.argv) > 1 else "mock"
    
    print(f"🧪 Stress Testing Streaming API with model: {model}")
    print("=" * 50)
    
    # Test 1: Burst of concurrent requests
    await run_concurrent_tests(10, model)
    print("\n" + "-" * 50)
    
    # Test 2: Higher concurrency
    await run_concurrent_tests(50, model)
    print("\n" + "-" * 50)
    
    # Test 3: Sustained load
    await run_sustained_load(30, 5.0, model)
    
    print("\n✅ Stress tests completed!")

if __name__ == "__main__":
    asyncio.run(main())