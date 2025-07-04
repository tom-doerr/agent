import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  Button,
  Paper,
  IconButton,
  Slider,
  Alert,
  Divider,
  Chip
} from '@mui/material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import {
  ThumbUp,
  ThumbDown,
  Refresh,
  DragHandle,
  Star,
  AutoAwesome
} from '@mui/icons-material';

function PreferenceUI({ images, onPreferenceUpdate, onGenerateOptimal }) {
  const [comparisonPair, setComparisonPair] = useState(null);
  const [rankings, setRankings] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [rating, setRating] = useState(0.5);
  const [message, setMessage] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    // Initialize rankings with latest images
    if (images.length > 0 && rankings.length === 0) {
      setRankings(images.slice(0, 10));
    }
  }, [images, rankings.length]);

  const selectRandomPair = async () => {
    if (images.length < 2) return;

    try {
      // Try to get smart suggestion from backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/preferences/suggest-comparison`);
      
      if (response.ok) {
        const suggestion = await response.json();
        const image1 = images.find(img => img.id === suggestion.image1_id);
        const image2 = images.find(img => img.id === suggestion.image2_id);
        
        if (image1 && image2) {
          setComparisonPair([image1, image2]);
          return;
        }
      }
    } catch (error) {
      console.log('Using random selection:', error);
    }

    // Fallback to random selection
    const indices = [];
    while (indices.length < 2) {
      const idx = Math.floor(Math.random() * images.length);
      if (!indices.includes(idx)) {
        indices.push(idx);
      }
    }

    setComparisonPair([images[indices[0]], images[indices[1]]]);
  };

  const handleComparison = async (winnerId, loserId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/preferences/compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          winner_id: winnerId,
          loser_id: loserId,
          comparison_type: 'a_b_test',
        }),
      });

      if (response.ok) {
        setMessage('Preference recorded!');
        setTimeout(() => setMessage(null), 2000);
        selectRandomPair();
        onPreferenceUpdate();
      }
    } catch (error) {
      console.error('Error submitting comparison:', error);
    }
  };

  const handleRating = async () => {
    if (!selectedImage) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/preferences/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_id: selectedImage.id,
          score: rating,
          feedback_type: 'rating',
        }),
      });

      if (response.ok) {
        setMessage('Rating submitted!');
        setTimeout(() => setMessage(null), 2000);
        setSelectedImage(null);
        setRating(0.5);
        onPreferenceUpdate();
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
    }
  };

  const handleDragEnd = async (result) => {
    if (!result.destination) return;

    const items = Array.from(rankings);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setRankings(items);

    // Submit new ranking
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/preferences/rank`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_rankings: items.map(img => img.id),
        }),
      });

      if (response.ok) {
        setMessage('Rankings updated!');
        setTimeout(() => setMessage(null), 2000);
        onPreferenceUpdate();
      }
    } catch (error) {
      console.error('Error updating rankings:', error);
    }
  };

  const handleGenerateOptimal = async () => {
    setGenerating(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/generate/optimal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const status = await response.json();
        setMessage('Generating optimal image based on your preferences...');
        setTimeout(() => setMessage(null), 3000);
        if (onGenerateOptimal) {
          onGenerateOptimal(status.task_id);
        }
      }
    } catch (error) {
      console.error('Error generating optimal image:', error);
      setMessage('Failed to generate image');
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Box>
      {message && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      {/* Generate Optimal Image Button */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<AutoAwesome />}
          onClick={handleGenerateOptimal}
          disabled={generating || images.length < 3}
          sx={{ 
            background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
            boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
            color: 'white',
            '&:hover': {
              background: 'linear-gradient(45deg, #FE6B8B 60%, #FF8E53 100%)',
            }
          }}
        >
          Generate Image Based on My Preferences
        </Button>
        {images.length < 3 && (
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Rate or compare at least 3 images to enable preference-based generation
          </Typography>
        )}
      </Box>

      {/* A/B Comparison */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          A/B Comparison
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Choose which image you prefer. This helps the system learn your preferences.
        </Typography>

        {!comparisonPair ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Button
              variant="contained"
              onClick={selectRandomPair}
              startIcon={<Refresh />}
              disabled={images.length < 2}
            >
              Start Comparison
            </Button>
            {images.length < 2 && (
              <Typography variant="caption" display="block" sx={{ mt: 2 }}>
                Generate at least 2 images to start comparing
              </Typography>
            )}
          </Box>
        ) : (
          <Grid container spacing={2} sx={{ mt: 2 }}>
            {comparisonPair.map((image, index) => (
              <Grid item xs={12} md={6} key={image.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    transition: 'transform 0.2s',
                    '&:hover': { transform: 'scale(1.02)' },
                  }}
                  onClick={() => handleComparison(
                    image.id,
                    comparisonPair[1 - index].id
                  )}
                >
                  <CardMedia
                    component="img"
                    height="300"
                    image={image.url}
                    alt={image.prompt}
                  />
                  <CardContent>
                    <Typography variant="body2" noWrap>
                      {image.prompt}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      <Divider sx={{ my: 4 }} />

      {/* Absolute Rating */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Rate Images
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Give individual ratings to images on a scale of 0 to 1.
        </Typography>

        {!selectedImage ? (
          <Grid container spacing={2} sx={{ mt: 2 }}>
            {images.slice(0, 8).map((image) => (
              <Grid item xs={6} sm={3} key={image.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    transition: 'transform 0.2s',
                    '&:hover': { transform: 'scale(1.05)' },
                  }}
                  onClick={() => setSelectedImage(image)}
                >
                  <CardMedia
                    component="img"
                    height="150"
                    image={image.url}
                    alt={image.prompt}
                  />
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardMedia
                    component="img"
                    image={selectedImage.url}
                    alt={selectedImage.prompt}
                    sx={{ maxHeight: 400 }}
                  />
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body1" gutterBottom>
                  {selectedImage.prompt}
                </Typography>
                <Box sx={{ mt: 4 }}>
                  <Typography gutterBottom>
                    Rating: {rating.toFixed(2)}
                  </Typography>
                  <Slider
                    value={rating}
                    onChange={(e, v) => setRating(v)}
                    step={0.1}
                    marks
                    min={0}
                    max={1}
                    valueLabelDisplay="auto"
                  />
                  <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                    <Button
                      variant="contained"
                      onClick={handleRating}
                      startIcon={<Star />}
                    >
                      Submit Rating
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        setSelectedImage(null);
                        setRating(0.5);
                      }}
                    >
                      Cancel
                    </Button>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      <Divider sx={{ my: 4 }} />

      {/* Drag and Drop Ranking */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Rank Your Favorites
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Drag and drop to order images from best (top) to worst (bottom).
        </Typography>

        {rankings.length > 0 ? (
          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="rankings">
              {(provided) => (
                <Box
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  sx={{ mt: 2 }}
                >
                  {rankings.map((image, index) => (
                    <Draggable key={image.id} draggableId={image.id} index={index}>
                      {(provided, snapshot) => (
                        <Card
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          sx={{
                            mb: 2,
                            backgroundColor: snapshot.isDragging ? 'action.hover' : 'background.paper',
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
                            <IconButton
                              {...provided.dragHandleProps}
                              sx={{ mr: 2 }}
                            >
                              <DragHandle />
                            </IconButton>
                            <Typography sx={{ mr: 2, minWidth: 30 }}>
                              #{index + 1}
                            </Typography>
                            <Box
                              component="img"
                              src={image.url}
                              alt={image.prompt}
                              sx={{ width: 80, height: 80, objectFit: 'cover', mr: 2 }}
                            />
                            <Typography variant="body2" sx={{ flexGrow: 1 }} noWrap>
                              {image.prompt}
                            </Typography>
                            <Chip
                              label={image.provider}
                              size="small"
                              sx={{ ml: 2 }}
                            />
                          </Box>
                        </Card>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </Box>
              )}
            </Droppable>
          </DragDropContext>
        ) : (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
            No images available for ranking. Generate some images first!
          </Typography>
        )}
      </Paper>
    </Box>
  );
}

export default PreferenceUI;