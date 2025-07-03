#!/usr/bin/env python3
"""
Hacker News API client for fetching real stories.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from datetime import datetime


@dataclass
class HNStory:
    """Represents a Hacker News story."""
    id: int
    title: str
    url: str
    score: int
    by: str
    time: int
    descendants: int
    type: str = "story"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'score': self.score,
            'by': self.by,
            'time': self.time,
            'descendants': self.descendants,
            'type': self.type
        }
    
    def age_hours(self) -> float:
        """Get age in hours."""
        return (time.time() - self.time) / 3600
    
    def to_text(self) -> str:
        """Convert to text for embedding."""
        age = self.age_hours()
        if age < 1:
            age_str = f"{int(age * 60)} minutes"
        elif age < 24:
            age_str = f"{int(age)} hours"
        else:
            age_str = f"{int(age / 24)} days"
            
        return f"{self.title} ({self.score} points by {self.by}, {self.descendants} comments, {age_str} ago)"


class HNAPIClient:
    """Async client for Hacker News API."""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_item(self, session: aiohttp.ClientSession, item_id: int) -> Optional[dict]:
        """Fetch a single item."""
        async with self.semaphore:
            try:
                url = f"{self.BASE_URL}/item/{item_id}.json"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception as e:
                print(f"Error fetching item {item_id}: {e}")
            return None
    
    async def fetch_story(self, session: aiohttp.ClientSession, story_id: int) -> Optional[HNStory]:
        """Fetch a story and convert to HNStory object."""
        data = await self.fetch_item(session, story_id)
        if data and data.get('type') == 'story' and not data.get('dead'):
            try:
                return HNStory(
                    id=data['id'],
                    title=data.get('title', 'Untitled'),
                    url=data.get('url', ''),
                    score=data.get('score', 0),
                    by=data.get('by', 'unknown'),
                    time=data.get('time', 0),
                    descendants=data.get('descendants', 0)
                )
            except:
                pass
        return None
    
    async def fetch_top_stories(self, limit: int = 30) -> List[HNStory]:
        """Fetch current top stories."""
        async with aiohttp.ClientSession() as session:
            # Get top story IDs
            url = f"{self.BASE_URL}/topstories.json"
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                story_ids = await response.json()
            
            # Fetch stories in parallel
            story_ids = story_ids[:limit]
            tasks = [self.fetch_story(session, sid) for sid in story_ids]
            stories = await asyncio.gather(*tasks)
            
            # Filter out None values
            return [s for s in stories if s is not None]
    
    async def fetch_new_stories(self, limit: int = 30) -> List[HNStory]:
        """Fetch newest stories."""
        async with aiohttp.ClientSession() as session:
            # Get new story IDs
            url = f"{self.BASE_URL}/newstories.json"
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                story_ids = await response.json()
            
            # Fetch stories in parallel
            story_ids = story_ids[:limit]
            tasks = [self.fetch_story(session, sid) for sid in story_ids]
            stories = await asyncio.gather(*tasks)
            
            # Filter out None values
            return [s for s in stories if s is not None]
    
    async def fetch_best_stories(self, limit: int = 30) -> List[HNStory]:
        """Fetch best stories."""
        async with aiohttp.ClientSession() as session:
            # Get best story IDs
            url = f"{self.BASE_URL}/beststories.json"
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                story_ids = await response.json()
            
            # Fetch stories in parallel
            story_ids = story_ids[:limit]
            tasks = [self.fetch_story(session, sid) for sid in story_ids]
            stories = await asyncio.gather(*tasks)
            
            # Filter out None values
            return [s for s in stories if s is not None]
    
    async def fetch_show_stories(self, limit: int = 30) -> List[HNStory]:
        """Fetch Show HN stories."""
        async with aiohttp.ClientSession() as session:
            # Get show story IDs
            url = f"{self.BASE_URL}/showstories.json"
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                story_ids = await response.json()
            
            # Fetch stories in parallel
            story_ids = story_ids[:limit]
            tasks = [self.fetch_story(session, sid) for sid in story_ids]
            stories = await asyncio.gather(*tasks)
            
            # Filter out None values and ensure they're Show HN
            show_stories = []
            for s in stories:
                if s and s.title.startswith("Show HN"):
                    show_stories.append(s)
            
            return show_stories


async def demo():
    """Demo the HN API client."""
    client = HNAPIClient()
    
    print("Fetching top stories...")
    top_stories = await client.fetch_top_stories(10)
    
    print(f"\nTop {len(top_stories)} stories:")
    for i, story in enumerate(top_stories, 1):
        print(f"{i}. [{story.score}] {story.title}")
        print(f"   by {story.by} | {story.descendants} comments | {story.age_hours():.1f} hours ago")
    
    print("\n" + "="*60 + "\n")
    
    print("Fetching newest stories...")
    new_stories = await client.fetch_new_stories(5)
    
    print(f"\nNewest {len(new_stories)} stories:")
    for story in new_stories:
        print(f"- {story.title}")
        print(f"  {story.score} points | {story.age_hours():.1f} hours ago")
    
    # Save sample data
    sample_data = {
        'timestamp': datetime.now().isoformat(),
        'top_stories': [s.to_dict() for s in top_stories],
        'new_stories': [s.to_dict() for s in new_stories]
    }
    
    with open('hn_sample_data.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print("\nSample data saved to hn_sample_data.json")


if __name__ == "__main__":
    asyncio.run(demo())