#!/usr/bin/env python3
"""Tests for HN API client."""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import time

from hn_api_client import HNAPIClient, HNStory


class TestHNStory:
    """Test HNStory dataclass."""
    
    def test_creation(self):
        """Test creating HNStory instance."""
        story = HNStory(
            id=123,
            title="Test Story",
            url="https://example.com",
            score=100,
            by="testuser",
            time=1234567890,
            descendants=50
        )
        
        assert story.id == 123
        assert story.title == "Test Story"
        assert story.url == "https://example.com"
        assert story.score == 100
        assert story.by == "testuser"
        assert story.time == 1234567890
        assert story.descendants == 50
        assert story.type == "story"
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        story = HNStory(
            id=123,
            title="Test Story",
            url="https://example.com",
            score=100,
            by="testuser",
            time=1234567890,
            descendants=50
        )
        
        d = story.to_dict()
        assert isinstance(d, dict)
        assert d['id'] == 123
        assert d['title'] == "Test Story"
        assert d['url'] == "https://example.com"
        assert d['score'] == 100
        assert d['by'] == "testuser"
        assert d['time'] == 1234567890
        assert d['descendants'] == 50
        assert d['type'] == "story"
    
    def test_age_hours(self):
        """Test age calculation."""
        # Create story from 2 hours ago
        current_time = time.time()
        two_hours_ago = current_time - (2 * 3600)
        
        story = HNStory(
            id=123,
            title="Test",
            url="",
            score=0,
            by="test",
            time=int(two_hours_ago),
            descendants=0
        )
        
        age = story.age_hours()
        assert 1.9 < age < 2.1  # Allow some tolerance
    
    def test_to_text(self):
        """Test text representation for embedding."""
        story = HNStory(
            id=123,
            title="Test Story",
            url="https://example.com",
            score=100,
            by="testuser",
            time=int(time.time() - 3600),  # 1 hour ago
            descendants=50
        )
        
        text = story.to_text()
        assert "Test Story" in text
        assert "100 points" in text
        assert "testuser" in text
        assert "50 comments" in text
        assert "hour" in text or "minutes" in text


class TestHNAPIClient:
    """Test HN API client."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return HNAPIClient(max_concurrent=5)
    
    @pytest.mark.asyncio
    async def test_initialization(self, client):
        """Test client initialization."""
        assert client.max_concurrent == 5
        assert isinstance(client.semaphore, asyncio.Semaphore)
        assert client.BASE_URL == "https://hacker-news.firebaseio.com/v0"
    
    @pytest.mark.asyncio
    async def test_fetch_item_success(self, client):
        """Test successful item fetch."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'id': 123,
            'type': 'story',
            'title': 'Test Story',
            'score': 100
        })
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        
        result = await client.fetch_item(mock_session, 123)
        
        assert result is not None
        assert result['id'] == 123
        assert result['type'] == 'story'
        assert result['title'] == 'Test Story'
    
    @pytest.mark.asyncio
    async def test_fetch_item_failure(self, client):
        """Test failed item fetch."""
        mock_response = AsyncMock()
        mock_response.status = 404
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            session = MagicMock()
            result = await client.fetch_item(session, 999)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_story_valid(self, client):
        """Test fetching valid story."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'id': 123,
            'type': 'story',
            'title': 'Test Story',
            'url': 'https://example.com',
            'score': 100,
            'by': 'testuser',
            'time': 1234567890,
            'descendants': 50
        })
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        
        result = await client.fetch_story(mock_session, 123)
        
        assert isinstance(result, HNStory)
        assert result.id == 123
        assert result.title == 'Test Story'
        assert result.score == 100
    
    @pytest.mark.asyncio
    async def test_fetch_story_dead(self, client):
        """Test fetching dead story returns None."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'id': 123,
            'type': 'story',
            'title': 'Test Story',
            'dead': True
        })
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            session = MagicMock()
            result = await client.fetch_story(session, 123)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_story_not_story_type(self, client):
        """Test fetching non-story returns None."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'id': 123,
            'type': 'comment',
            'text': 'This is a comment'
        })
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            session = MagicMock()
            result = await client.fetch_story(session, 123)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_top_stories(self, client):
        """Test fetching top stories."""
        # Mock the story IDs response
        mock_ids_response = AsyncMock()
        mock_ids_response.status = 200
        mock_ids_response.json = AsyncMock(return_value=[123, 124, 125, 126, 127])
        
        # Mock individual story responses
        story_data = {
            123: {'id': 123, 'type': 'story', 'title': 'Story 1', 'score': 100, 'by': 'user1', 'time': 1234567890, 'descendants': 10},
            124: {'id': 124, 'type': 'story', 'title': 'Story 2', 'score': 90, 'by': 'user2', 'time': 1234567891, 'descendants': 20},
            125: {'id': 125, 'type': 'story', 'title': 'Story 3', 'score': 80, 'by': 'user3', 'time': 1234567892, 'descendants': 30},
        }
        
        def mock_get(url):
            mock_resp = AsyncMock()
            if url.endswith('topstories.json'):
                mock_resp.status = 200
                mock_resp.json = AsyncMock(return_value=[123, 124, 125, 126, 127])
            else:
                # Extract ID from URL
                story_id = int(url.split('/')[-1].replace('.json', ''))
                mock_resp.status = 200
                mock_resp.json = AsyncMock(return_value=story_data.get(story_id, {'type': 'comment'}))
            
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock(return_value=None)
            return mock_resp
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get = Mock(side_effect=mock_get)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session
            
            stories = await client.fetch_top_stories(3)
            
            assert len(stories) == 3
            assert all(isinstance(s, HNStory) for s in stories)
            assert stories[0].id == 123
            assert stories[1].id == 124
            assert stories[2].id == 125
    
    @pytest.mark.asyncio
    async def test_fetch_new_stories(self, client):
        """Test fetching new stories."""
        # Similar to top stories but different endpoint
        mock_ids_response = AsyncMock()
        mock_ids_response.status = 200
        mock_ids_response.json = AsyncMock(return_value=[200, 201, 202])
        
        story_data = {
            200: {'id': 200, 'type': 'story', 'title': 'New Story 1', 'score': 5, 'by': 'newuser1', 'time': 1234567900, 'descendants': 0},
            201: {'id': 201, 'type': 'story', 'title': 'New Story 2', 'score': 3, 'by': 'newuser2', 'time': 1234567901, 'descendants': 1},
        }
        
        def mock_get(url):
            mock_resp = AsyncMock()
            if url.endswith('newstories.json'):
                mock_resp.status = 200
                mock_resp.json = AsyncMock(return_value=[200, 201, 202])
            else:
                story_id = int(url.split('/')[-1].replace('.json', ''))
                mock_resp.status = 200
                mock_resp.json = AsyncMock(return_value=story_data.get(story_id, {'type': 'comment'}))
            
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock(return_value=None)
            return mock_resp
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get = Mock(side_effect=mock_get)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session
            
            stories = await client.fetch_new_stories(2)
            
            assert len(stories) == 2
            assert stories[0].title == 'New Story 1'
            assert stories[1].title == 'New Story 2'
    
    @pytest.mark.asyncio
    async def test_fetch_show_stories(self, client):
        """Test fetching Show HN stories."""
        mock_ids_response = AsyncMock()
        mock_ids_response.status = 200
        mock_ids_response.json = AsyncMock(return_value=[300, 301, 302])
        
        story_data = {
            300: {'id': 300, 'type': 'story', 'title': 'Show HN: My Project', 'score': 50, 'by': 'maker1', 'time': 1234567900, 'descendants': 10},
            301: {'id': 301, 'type': 'story', 'title': 'Regular Story', 'score': 40, 'by': 'user1', 'time': 1234567901, 'descendants': 5},
            302: {'id': 302, 'type': 'story', 'title': 'Show HN: Another Project', 'score': 30, 'by': 'maker2', 'time': 1234567902, 'descendants': 8},
        }
        
        def mock_get(url):
            mock_resp = AsyncMock()
            if url.endswith('showstories.json'):
                mock_resp.status = 200
                mock_resp.json = AsyncMock(return_value=[300, 301, 302])
            else:
                story_id = int(url.split('/')[-1].replace('.json', ''))
                mock_resp.status = 200
                mock_resp.json = AsyncMock(return_value=story_data.get(story_id, {'type': 'comment'}))
            
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock(return_value=None)
            return mock_resp
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get = Mock(side_effect=mock_get)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session
            
            stories = await client.fetch_show_stories(3)
            
            # Should only return Show HN stories
            assert len(stories) == 2
            assert all(s.title.startswith("Show HN") for s in stories)
            assert stories[0].id == 300
            assert stories[1].id == 302
    
    @pytest.mark.asyncio
    async def test_concurrent_limit(self, client):
        """Test concurrent request limiting."""
        client = HNAPIClient(max_concurrent=2)
        
        # Track concurrent requests
        concurrent_count = 0
        max_concurrent_seen = 0
        
        async def mock_get(url):
            nonlocal concurrent_count, max_concurrent_seen
            concurrent_count += 1
            max_concurrent_seen = max(max_concurrent_seen, concurrent_count)
            
            # Simulate some delay
            await asyncio.sleep(0.1)
            
            concurrent_count -= 1
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'type': 'comment'})
            return mock_response
        
        with patch('aiohttp.ClientSession.get', side_effect=mock_get):
            session = MagicMock()
            # Fire off multiple requests
            tasks = [client.fetch_item(session, i) for i in range(5)]
            await asyncio.gather(*tasks)
            
            # Should never exceed max_concurrent
            assert max_concurrent_seen <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])