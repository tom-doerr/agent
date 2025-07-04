import pytest

def test_simple():
    assert 1 + 1 == 2

@pytest.mark.asyncio
async def test_async_simple():
    import asyncio
    await asyncio.sleep(0.1)
    assert True