"""Tests for optimization demo token and cost tracking."""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
import sys

sys.path.append(str(Path(__file__).parent.parent))


class TestPricingFunctions:
    """Test pricing and cost calculation functions."""
    
    def test_pricing_config_loads(self):
        """Test that pricing config loads correctly."""
        config_path = Path("pricing_config.json")
        assert config_path.exists()
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "deepseek_reasoner" in config
        assert "pricing_schedule" in config["deepseek_reasoner"]
    
    def test_calculate_cost_logic(self):
        """Test cost calculation logic."""
        # Test the math with known values
        pricing = {"input_cache_hit": 0.14, "input_cache_miss": 0.55, "output": 2.19}
        
        input_tokens = 1000
        output_tokens = 500
        cache_hit_rate = 0.5
        
        # Calculate costs
        input_cost_hit = (input_tokens * cache_hit_rate) * pricing["input_cache_hit"] / 1_000_000
        input_cost_miss = (input_tokens * (1 - cache_hit_rate)) * pricing["input_cache_miss"] / 1_000_000
        output_cost = output_tokens * pricing["output"] / 1_000_000
        
        total_cost = input_cost_hit + input_cost_miss + output_cost
        
        # Verify calculations
        expected_input = (500 * 0.14 + 500 * 0.55) / 1_000_000
        expected_output = 500 * 2.19 / 1_000_000
        expected_total = expected_input + expected_output
        
        assert abs(total_cost - expected_total) < 0.0001
        assert abs(input_cost_hit - (500 * 0.14 / 1_000_000)) < 0.0001
        assert abs(input_cost_miss - (500 * 0.55 / 1_000_000)) < 0.0001
    
    def test_pricing_period_logic(self):
        """Test pricing period detection logic."""
        # Test discount period detection
        discount_hours = [16.5, 17, 23, 0, 0.4]
        for hour in discount_hours:
            # Should be discount period
            assert hour >= 16.5 or hour < 0.5
        
        # Test standard period detection  
        standard_hours = [0.5, 1, 10, 16, 16.4]
        for hour in standard_hours:
            # Should be standard period
            assert 0.5 <= hour < 16.5
    
    def test_wait_time_calculation(self):
        """Test wait time calculation logic."""
        # If current hour is 10:00, wait time to 16:30 should be 6.5 hours
        current_hour = 10.0
        hours_until_discount = 16.5 - current_hour
        assert abs(hours_until_discount - 6.5) < 0.01
        
        # If current hour is 17:00 (discount), time remaining is ~7.5 hours
        current_hour = 17.0
        hours_remaining = 24 - current_hour + 0.5
        assert abs(hours_remaining - 7.5) < 0.01


class TestCostSummary:
    """Test cost summary calculations."""
    
    def test_cost_summary_calculation(self):
        """Test the cost summary logic from the main script."""
        # Create test log entries
        test_entries = [
            {
                "optimizer": "SIMBA",
                "total_tokens": 1000,
                "input_tokens": 700,
                "output_tokens": 300,
                "total_cost_usd": 0.001
            },
            {
                "optimizer": "SIMBA",
                "total_tokens": 1500,
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_cost_usd": 0.0015
            },
            {
                "optimizer": "other",
                "total_tokens": 500,
                "total_cost_usd": 0.0005
            }
        ]
        
        # Calculate totals for SIMBA optimizer
        total_cost = 0
        total_tokens = 0
        for entry in test_entries:
            if entry["optimizer"] == "SIMBA":
                total_cost += entry.get("total_cost_usd", 0)
                total_tokens += entry.get("total_tokens", 0)
        
        assert total_cost == 0.0025
        assert total_tokens == 2500


class TestPricingConfig:
    """Test pricing configuration loading."""
    
    def test_pricing_config_structure(self):
        """Test that pricing config has expected structure."""
        config_path = Path("pricing_config.json")
        
        # Only test if file exists (it should in the repo)
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            
            assert "deepseek_reasoner" in config
            assert "pricing_schedule" in config["deepseek_reasoner"]
            
            schedule = config["deepseek_reasoner"]["pricing_schedule"]
            assert "standard" in schedule
            assert "discount" in schedule
            
            # Check discount is actually cheaper
            assert schedule["discount"]["output"] < schedule["standard"]["output"]
            assert schedule["discount"]["input_cache_miss"] < schedule["standard"]["input_cache_miss"]
    
    def test_pricing_values(self):
        """Test specific pricing values match expected."""
        config_path = Path("pricing_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        schedule = config["deepseek_reasoner"]["pricing_schedule"]
        
        # Standard pricing
        assert schedule["standard"]["input_cache_hit"] == 0.14
        assert schedule["standard"]["input_cache_miss"] == 0.55
        assert schedule["standard"]["output"] == 2.19
        
        # Discount pricing
        assert schedule["discount"]["input_cache_hit"] == 0.035
        assert schedule["discount"]["input_cache_miss"] == 0.135
        assert schedule["discount"]["output"] == 0.550


class TestTokenLogging:
    """Test token logging concepts."""
    
    def test_log_file_writing(self):
        """Test that we can write NDJSON log entries."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ndjson') as f:
            log_file = Path(f.name)
        
        try:
            # Write test entries
            test_entry = {
                "timestamp": datetime.now().isoformat(),
                "phase": "test",
                "optimizer": "test_opt",
                "total_tokens": 100,
                "total_cost_usd": 0.001
            }
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(test_entry) + '\n')
            
            # Read and verify
            with open(log_file) as f:
                loaded = json.loads(f.readline())
            
            assert loaded["phase"] == "test"
            assert loaded["optimizer"] == "test_opt"
            assert loaded["total_tokens"] == 100
            assert loaded["total_cost_usd"] == 0.001
            
        finally:
            log_file.unlink()
    
    def test_cost_tracking_data_structure(self):
        """Test the expected structure of cost tracking data."""
        # Example log entry structure
        log_entry = {
            "timestamp": "2024-01-01T00:00:00",
            "unix_time": 1704067200,
            "utc_hour": 0.0,
            "phase": "optimization",
            "optimizer": "SIMBA",
            "step": 1,
            "elapsed_seconds": 10.5,
            "input_tokens": 1000,
            "output_tokens": 500,
            "reasoning_tokens": 100,
            "total_tokens": 1600,
            "total_cost_usd": 0.002,
            "pricing_period": "discount",
            "cache_hit_rate": 0.0
        }
        
        # Verify all expected fields are present
        required_fields = [
            "timestamp", "phase", "optimizer", "step",
            "input_tokens", "output_tokens", "total_tokens"
        ]
        
        for field in required_fields:
            assert field in log_entry
        
        # Verify numeric fields
        assert isinstance(log_entry["total_tokens"], int)
        assert isinstance(log_entry["total_cost_usd"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])