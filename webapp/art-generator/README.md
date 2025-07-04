# AI Art Generator with Preference Learning

An intelligent image generation system that learns your aesthetic preferences through interactive feedback. Generate AI art using multiple providers (OpenAI DALL-E, Stable Diffusion) and train the system to understand what you like through A/B comparisons, ratings, and rankings.

## Features

- **Multi-Provider Image Generation**: Support for OpenAI DALL-E 3 and Stable Diffusion via Replicate
- **Preference Learning**: Three ways to teach the system your preferences:
  - A/B Comparisons: Choose between two images
  - Absolute Ratings: Rate images on a 0-1 scale
  - Drag-and-Drop Ranking: Order images from best to worst
- **Smart Recommendations**: The system learns to predict which images you'll like
- **Optimal Generation**: Generate new images optimized for your learned preferences
- **Real-time Updates**: WebSocket integration for live updates
- **Gallery with Filtering**: Browse, search, and sort your generated images

## Architecture

```
webapp/art-generator/
├── backend/          # FastAPI backend with preference learning
├── frontend/         # React frontend with Material-UI
├── e2e/             # End-to-end tests with Playwright
├── docker-compose.yml
└── nginx.conf
```

## Prerequisites

- Docker and Docker Compose
- API Keys (optional):
  - OpenAI API key (for DALL-E 3)
  - Replicate API token (for Stable Diffusion)

## Quick Start

### Option 1: Run Locally (No API Keys Required)

1. **Clone and navigate to the project**:
   ```bash
   cd webapp/art-generator
   ```

2. **Start the application**:
   ```bash
   docker-compose up
   ```

3. **Access the application**:
   - Frontend: http://localhost:3090
   - Backend API: http://localhost:8090
   - API Docs: http://localhost:8090/docs

**Note**: Without API keys, the system runs in mock mode, generating colorful gradient images with your prompt overlaid. This is perfect for testing the preference learning system!

### Option 2: Run with Real Image Generation

1. **Set up environment variables**:
   ```bash
   # Create a .env file in the art-generator directory
   echo "OPENAI_API_KEY=your-openai-key" >> .env
   echo "REPLICATE_API_TOKEN=your-replicate-token" >> .env
   ```

2. **Start the application**:
   ```bash
   docker-compose up
   ```

## Usage Guide

### 1. Generate Images

Navigate to the "Generate" tab:
- Enter a prompt describing what you want to see
- Choose a provider (OpenAI or Replicate)
- Select image size and style
- Click "Generate" to create an image

### 2. Teach Your Preferences

Navigate to "Compare & Learn" tab:

**A/B Comparison**:
- Click "Start Comparison"
- Click on the image you prefer
- The system learns from your choices

**Rate Images**:
- Click on any image thumbnail
- Adjust the rating slider (0-1)
- Submit your rating

**Rank Images**:
- Drag and drop images to order them
- Best images at the top, worst at bottom
- Rankings automatically update preferences

### 3. Browse and Filter

Navigate to "Gallery" tab:
- Search images by prompt text
- Sort by newest, oldest, or predicted preference
- Filter by provider
- View prediction scores for each image

### 4. Generate Optimal Images

After rating at least 5 images:
- Click "Generate Optimal" in the Generate tab
- The system will create images based on your learned preferences

## Development

### Running Tests

**Backend Tests**:
```bash
docker-compose -f docker-compose.test.yml run backend-test
```

**Frontend Tests**:
```bash
docker-compose -f docker-compose.test.yml run frontend-test
```

**E2E Tests**:
```bash
docker-compose -f docker-compose.test.yml run e2e-test
```

### Local Development

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
npm start
```

## API Documentation

The backend provides a comprehensive REST API:

- `POST /generate` - Generate a new image
- `GET /status/{task_id}` - Check generation status
- `GET /images` - List all generated images
- `POST /preferences/compare` - Submit A/B comparison
- `POST /preferences/rate` - Submit absolute rating
- `POST /preferences/rank` - Submit ranking order
- `GET /predict/{image_id}` - Get preference prediction
- `POST /generate/optimal` - Generate optimized image

Full API documentation available at http://localhost:8090/docs

## Preference Learning Algorithm

The system uses a hybrid approach:
1. **ELO Rating System**: For pairwise comparisons
2. **Ridge Regression**: Maps image embeddings to preference scores
3. **Confidence Estimation**: Based on similarity to training data

The preference model is retrained automatically as you provide feedback.

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `REPLICATE_API_TOKEN`: Your Replicate API token
- `DATABASE_URL`: SQLite database path (default: `sqlite:///./data/preferences.db`)
- `CORS_ORIGINS`: Allowed CORS origins (default: `http://localhost:3090`)

### Docker Compose Services

- `backend`: FastAPI application (port 8090)
- `frontend`: React application (port 3090)
- `nginx`: Reverse proxy (port 80)

## Troubleshooting

**Images not generating**:
- Check API keys are correctly set
- Verify Docker containers are running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`

**Preference predictions not showing**:
- Generate and rate at least 5 images
- Refresh the gallery page
- Check browser console for errors

**WebSocket connection issues**:
- Ensure nginx is running
- Check WebSocket endpoint: ws://localhost/ws

## License

This project is part of the agent framework and follows its licensing terms.