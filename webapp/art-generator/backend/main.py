from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Optional
import asyncio
import uuid
from datetime import datetime
import json
import numpy as np

from database import init_db, get_session, ImageRecord
from models import (
    GenerationRequest, GeneratedImage, PreferenceComparison,
    UserPreference, RankingUpdate, PreferencePrediction,
    GenerationStatus, ImageProvider
)
from image_generator import ImageGenerator
from preference_learner import PreferenceLearner

app = FastAPI(title="AI Art Generator with Preference Learning")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3090", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
image_generator = ImageGenerator()
preference_learner = PreferenceLearner()

# Task storage
generation_tasks: Dict[str, GenerationStatus] = {}

# WebSocket connections
active_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()
    
    # Check available providers
    print("\n" + "="*60)
    print("🎨 Image Generation Providers:")
    
    if image_generator.openai_key:
        print("  ✅ OpenAI DALL-E 3: Available")
    else:
        print("  ❌ OpenAI DALL-E 3: No API key")
        
    if image_generator.replicate_token:
        print("  ✅ Replicate (Stable Diffusion): Available")
    else:
        print("  ❌ Replicate: No API token")
        
    if image_generator.local_available:
        print(f"  ✅ Local Model: Available at {image_generator.local_model_url}")
    else:
        print(f"  ❌ Local Model: Not detected at {image_generator.local_model_url}")
    
    if image_generator.mock_mode:
        print("\n  🎨 Mock Mode: Enabled (colorful gradients)")
        print("  Perfect for testing the preference learning system!")
    
    print("="*60 + "\n")
    
    # Try to load saved preference state
    try:
        preference_learner.load_state("data/preference_state.json")
        print("📊 Loaded saved preference state")
    except FileNotFoundError:
        pass


@app.on_event("shutdown")
async def shutdown_event():
    """Save preference state on shutdown."""
    preference_learner.save_state("data/preference_state.json")


@app.post("/generate", response_model=GenerationStatus)
async def generate_image(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    """Generate a new image based on the prompt."""
    
    task_id = str(uuid.uuid4())
    
    # Create initial status
    status = GenerationStatus(
        task_id=task_id,
        status="pending",
        progress=0.0
    )
    generation_tasks[task_id] = status
    
    # Start generation in background
    background_tasks.add_task(
        generate_image_task,
        task_id,
        request,
        session
    )
    
    return status


async def generate_image_task(
    task_id: str,
    request: GenerationRequest,
    session: AsyncSession,
    latent_vector: Optional[List[float]] = None
):
    """Background task to generate image."""
    
    try:
        # Update status
        generation_tasks[task_id].status = "processing"
        generation_tasks[task_id].progress = 0.1
        
        # Broadcast update
        await broadcast_update({"task_id": task_id, "status": "processing"})
        
        # Generate image
        image = await image_generator.generate_image(
            prompt=request.prompt,
            provider=request.provider,
            negative_prompt=request.negative_prompt,
            size=request.size,
            style=request.style,
            latent_vector=latent_vector
        )
        
        # Save to database
        db_image = ImageRecord(
            id=image.id,
            url=image.url,
            prompt=image.prompt,
            provider=image.provider.value,
            latent_vector=image.latent_vector,
            created_at=image.created_at,
            meta_data=image.metadata
        )
        session.add(db_image)
        await session.commit()
        
        # Update status
        generation_tasks[task_id].status = "completed"
        generation_tasks[task_id].progress = 1.0
        generation_tasks[task_id].result = image
        
        # Broadcast completion
        await broadcast_update({
            "task_id": task_id,
            "status": "completed",
            "image": jsonable_encoder(image)
        })
        
    except Exception as e:
        generation_tasks[task_id].status = "failed"
        generation_tasks[task_id].error = str(e)
        
        await broadcast_update({
            "task_id": task_id,
            "status": "failed",
            "error": str(e)
        })


@app.get("/status/{task_id}", response_model=GenerationStatus)
async def get_generation_status(task_id: str):
    """Get the status of a generation task."""
    
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return generation_tasks[task_id]


@app.get("/images", response_model=List[GeneratedImage])
async def get_images(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session)
):
    """Get all generated images."""
    
    result = await session.execute(
        select(ImageRecord)
        .order_by(ImageRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    images = result.scalars().all()
    
    return [
        GeneratedImage(
            id=img.id,
            url=img.url,
            prompt=img.prompt,
            provider=ImageProvider(img.provider),
            latent_vector=img.latent_vector,
            created_at=img.created_at,
            metadata=img.meta_data
        )
        for img in images
    ]


@app.get("/images/{image_id}", response_model=GeneratedImage)
async def get_image(
    image_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific image."""
    
    image = await session.get(ImageRecord, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return GeneratedImage(
        id=image.id,
        url=image.url,
        prompt=image.prompt,
        provider=ImageProvider(image.provider),
        latent_vector=image.latent_vector,
        created_at=image.created_at,
        metadata=image.meta_data
    )


@app.post("/preferences/compare")
async def submit_comparison(
    comparison: PreferenceComparison,
    session: AsyncSession = Depends(get_session)
):
    """Submit a pairwise comparison preference."""
    
    await preference_learner.add_comparison(
        session,
        comparison.winner_id,
        comparison.loser_id
    )
    
    # Broadcast preference update
    await broadcast_update({
        "type": "preference_update",
        "comparison": jsonable_encoder(comparison)
    })
    
    return {"status": "success"}


@app.post("/preferences/rate")
async def submit_rating(
    preference: UserPreference,
    session: AsyncSession = Depends(get_session)
):
    """Submit an absolute rating for an image."""
    
    await preference_learner.add_rating(
        session,
        preference.image_id,
        preference.score
    )
    
    return {"status": "success"}


@app.post("/preferences/rank")
async def update_ranking(
    ranking: RankingUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update image rankings based on drag-and-drop ordering."""
    
    # Convert ranking to pairwise comparisons
    for i in range(len(ranking.image_rankings) - 1):
        for j in range(i + 1, len(ranking.image_rankings)):
            winner_id = ranking.image_rankings[i]
            loser_id = ranking.image_rankings[j]
            
            await preference_learner.add_comparison(
                session,
                winner_id,
                loser_id
            )
    
    return {"status": "success", "comparisons_added": len(ranking.image_rankings) * (len(ranking.image_rankings) - 1) // 2}


@app.get("/predict/{image_id}", response_model=PreferencePrediction)
async def predict_preference(
    image_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Predict how much the user will like an image."""
    
    prediction = await preference_learner.predict_preference(session, image_id)
    return prediction


@app.get("/preferences/suggest-comparison")
async def suggest_comparison(
    session: AsyncSession = Depends(get_session)
):
    """Suggest the most informative pair of images to compare using active learning."""
    
    # Get recent images
    result = await session.execute(
        select(ImageRecord)
        .order_by(ImageRecord.created_at.desc())
        .limit(20)
    )
    images = result.scalars().all()
    
    if len(images) < 2:
        raise HTTPException(
            status_code=400,
            detail="Not enough images for comparison"
        )
    
    image_ids = [img.id for img in images]
    suggested_pair = await preference_learner.suggest_comparison_pair(session, image_ids)
    
    if not suggested_pair:
        # Fallback to random pair
        import random
        suggested_pair = random.sample(image_ids, 2)
    
    return {
        "image1_id": suggested_pair[0],
        "image2_id": suggested_pair[1],
        "reason": "Selected for maximum information gain"
    }


@app.post("/generate/optimal")
async def generate_optimal_image(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    base_prompt: Optional[str] = None
):
    """Generate an image optimized for user preferences."""
    
    # Get recent high-scoring images to understand preferences
    result = await session.execute(
        select(ImageRecord)
        .order_by(ImageRecord.created_at.desc())
        .limit(20)
    )
    recent_images = result.scalars().all()
    
    if not recent_images:
        raise HTTPException(
            status_code=400,
            detail="No images available to learn preferences from"
        )
    
    # Rank recent images
    image_ids = [img.id for img in recent_images]
    ranked = await preference_learner.get_ranked_images(session, image_ids)
    
    # Get top 3 images for latent vector averaging
    top_images = []
    for image_id, score in ranked[:3]:
        if score > 0.6:  # Only use images with good scores
            img = await session.get(ImageRecord, image_id)
            if img:
                top_images.append(img)
    
    if not top_images:
        # Fallback to most recent image
        top_images = [recent_images[0]]
    
    # Average latent vectors from top images
    averaged_latent = None
    if all(img.latent_vector for img in top_images):
        vectors = np.array([img.latent_vector for img in top_images])
        averaged_latent = np.mean(vectors, axis=0)
        # Normalize the averaged vector
        averaged_latent = averaged_latent / np.linalg.norm(averaged_latent)
        averaged_latent = averaged_latent.tolist()
    
    # Generate new prompt
    optimal_prompt = base_prompt or "An amazing artwork"
    
    # Create generation request with latent vector
    request = GenerationRequest(
        prompt=optimal_prompt,
        provider=ImageProvider(top_images[0].provider),
        size="1024x1024"
    )
    
    # Generate image
    task_id = str(uuid.uuid4())
    status = GenerationStatus(
        task_id=task_id,
        status="pending",
        progress=0.0
    )
    generation_tasks[task_id] = status
    
    # Pass latent vector to generation task
    background_tasks.add_task(
        generate_image_task,
        task_id,
        request,
        session,
        averaged_latent
    )
    
    return status


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def broadcast_update(data: dict):
    """Broadcast update to all connected clients."""
    
    message = json.dumps(data)
    
    # Send to all connected clients
    for connection in active_connections[:]:
        try:
            await connection.send_text(message)
        except:
            # Remove failed connections
            active_connections.remove(connection)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}