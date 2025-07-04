import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import httpx
from fastapi.testclient import TestClient
from main import app, generate_response

class TestStreamingPerformance:
    """Test streaming performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_streaming_latency(self):
        """Test first token latency"""
        latencies = []
        
        for _ in range(5):
            start_time = time.time()
            first_chunk_time = None
            
            async for event in generate_response("Hello", "mock"):
                if first_chunk_time is None and "chunk" in event:
                    first_chunk_time = time.time()
                    break
            
            if first_chunk_time:
                latency = first_chunk_time - start_time
                latencies.append(latency)
        
        # Average first token latency should be low
        avg_latency = statistics.mean(latencies)
        assert avg_latency < 0.1  # Less than 100ms
        print(f"Average first token latency: {avg_latency*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_token_throughput(self):
        """Test token generation throughput"""
        token_rates = []
        
        for _ in range(3):
            events = []
            async for event in generate_response("Generate a long response about Python programming", "mock"):
                events.append(event)
            
            # Parse final stats
            import json
            for event in events:
                if event.startswith("data: "):
                    data = json.loads(event[6:].strip())
                    if data.get("done") and "avg_tokens_per_sec" in data:
                        token_rates.append(data["avg_tokens_per_sec"])
                        break
        
        # Should maintain consistent token rate
        avg_rate = statistics.mean(token_rates)
        assert avg_rate > 10  # At least 10 tokens/second for mock
        print(f"Average token rate: {avg_rate:.2f} tokens/sec")
    
    def test_concurrent_streams(self):
        """Test handling multiple concurrent streams"""
        client = TestClient(app)
        
        def make_request(i):
            with client:
                response = client.get(f"/stream/Question{i}?model=mock", stream=True)
                chunks = 0
                for line in response.iter_lines():
                    if line.startswith(b"data: "):
                        chunks += 1
                return chunks
        
        # Test 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in futures]
            end_time = time.time()
        
        # All requests should complete
        assert all(chunks > 0 for chunks in results)
        
        # Should complete in reasonable time
        total_time = end_time - start_time
        assert total_time < 5.0  # Less than 5 seconds for 10 requests
        print(f"10 concurrent requests completed in {total_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test memory usage during streaming"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate 100 responses
        for i in range(100):
            events = []
            async for event in generate_response(f"Question {i}", "mock"):
                events.append(event)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 50  # Less than 50MB increase
        print(f"Memory increase after 100 responses: {memory_increase:.2f}MB")

class TestEndpointPerformance:
    """Test API endpoint performance"""
    
    def test_models_endpoint_performance(self):
        """Test /models endpoint response time"""
        client = TestClient(app)
        
        response_times = []
        for _ in range(100):
            start = time.time()
            response = client.get("/models")
            end = time.time()
            
            assert response.status_code == 200
            response_times.append(end - start)
        
        avg_time = statistics.mean(response_times)
        p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        assert avg_time < 0.01  # Less than 10ms average
        assert p95_time < 0.02  # Less than 20ms for 95th percentile
        print(f"Models endpoint - Avg: {avg_time*1000:.2f}ms, P95: {p95_time*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_streaming_backpressure(self):
        """Test streaming handles slow clients properly"""
        slow_client_events = []
        
        async for event in generate_response("Generate response", "mock"):
            slow_client_events.append(event)
            # Simulate slow client
            await asyncio.sleep(0.05)
        
        # Should still complete successfully
        assert len(slow_client_events) > 0
        
        # Parse events
        import json
        parsed = [json.loads(e[6:].strip()) for e in slow_client_events if e.startswith("data: ")]
        done_events = [e for e in parsed if e.get("done")]
        assert len(done_events) == 1

class TestStressTests:
    """Stress tests for the streaming system"""
    
    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """Test system under sustained load"""
        async def make_async_request(session, i):
            try:
                async with session.get(f"http://localhost:8000/stream/Question{i}?model=mock") as response:
                    chunks = 0
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunks += 1
                    return chunks > 0
            except Exception as e:
                print(f"Request {i} failed: {e}")
                return False
        
        # Run 100 requests over 10 seconds
        async with httpx.AsyncClient() as session:
            tasks = []
            for i in range(100):
                tasks.append(make_async_request(session, i))
                await asyncio.sleep(0.1)  # Space out requests
            
            results = await asyncio.gather(*tasks)
        
        # At least 90% should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.9
        print(f"Success rate under load: {success_rate*100:.1f}%")
    
    @pytest.mark.stress
    def test_rapid_connections(self):
        """Test rapid connection/disconnection"""
        client = TestClient(app)
        
        successes = 0
        failures = 0
        
        for i in range(50):
            try:
                with client as c:
                    # Start streaming then immediately close
                    with c.stream("GET", f"/stream/Q{i}?model=mock") as response:
                        for line in response.iter_lines():
                            if line.startswith(b"data: "):
                                # Close after first chunk
                                break
                successes += 1
            except Exception:
                failures += 1
        
        # Should handle rapid connections gracefully
        assert successes > 45  # At least 90% success
        print(f"Rapid connection test: {successes} successes, {failures} failures")

# Performance benchmark runner
if __name__ == "__main__":
    print("Running performance benchmarks...")
    
    # Run basic performance tests
    perf_test = TestStreamingPerformance()
    asyncio.run(perf_test.test_streaming_latency())
    asyncio.run(perf_test.test_token_throughput())
    perf_test.test_concurrent_streams()
    
    # Run endpoint tests
    endpoint_test = TestEndpointPerformance()
    endpoint_test.test_models_endpoint_performance()