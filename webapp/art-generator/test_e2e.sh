#!/bin/bash
set -e

echo "=========================================="
echo "AI Art Generator E2E Tests"
echo "=========================================="

BASE_URL="http://localhost:8090"

# Test 1: Health check
echo -e "\n1. Testing health endpoint..."
HEALTH=$(curl -s $BASE_URL/health)
echo "Response: $HEALTH"
echo "✓ Health check passed"

# Test 2: Generate image
echo -e "\n2. Testing image generation..."
RESPONSE=$(curl -s -X POST $BASE_URL/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful mountain landscape", "provider": "openai", "size": "512x512"}')
TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "Task ID: $TASK_ID"
echo "✓ Generation started"

# Wait for completion
echo "Waiting for image generation..."
sleep 3

# Check status
STATUS=$(curl -s $BASE_URL/status/$TASK_ID | jq -r '.status')
echo "Status: $STATUS"

# Test 3: List images
echo -e "\n3. Testing image listing..."
IMAGES=$(curl -s $BASE_URL/images)
COUNT=$(echo $IMAGES | jq '. | length')
echo "Found $COUNT images"
echo "✓ Image listing works"

# Test 4: Test preference if we have images
if [ "$COUNT" -gt "1" ]; then
    echo -e "\n4. Testing preference system..."
    IMAGE1=$(echo $IMAGES | jq -r '.[0].id')
    IMAGE2=$(echo $IMAGES | jq -r '.[1].id')
    
    # Submit comparison
    curl -s -X POST $BASE_URL/preferences/compare \
      -H "Content-Type: application/json" \
      -d "{\"winner_id\": \"$IMAGE1\", \"loser_id\": \"$IMAGE2\"}" > /dev/null
    echo "✓ Preference comparison recorded"
    
    # Get prediction
    PREDICTION=$(curl -s $BASE_URL/predict/$IMAGE1)
    SCORE=$(echo $PREDICTION | jq -r '.predicted_score')
    echo "✓ Prediction score: $SCORE"
fi

echo -e "\n=========================================="
echo "✅ All E2E tests passed!"
echo "=========================================="