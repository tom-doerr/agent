import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  Search,
  FilterList,
  Refresh,
  Download,
  Favorite,
  FavoriteBorder,
  ZoomIn,
  AutoAwesome
} from '@mui/icons-material';

function Gallery({ images, onRefresh }) {
  const [filteredImages, setFilteredImages] = useState(images);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [filterProvider, setFilterProvider] = useState('all');
  const [selectedImage, setSelectedImage] = useState(null);
  const [predictions, setPredictions] = useState({});
  const [loadingPredictions, setLoadingPredictions] = useState(false);

  useEffect(() => {
    filterAndSortImages();
  }, [images, searchTerm, sortBy, filterProvider]);

  useEffect(() => {
    // Load predictions for visible images
    if (filteredImages.length > 0 && Object.keys(predictions).length === 0) {
      loadPredictions();
    }
  }, [filteredImages]);

  const filterAndSortImages = () => {
    let filtered = [...images];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(img =>
        img.prompt.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply provider filter
    if (filterProvider !== 'all') {
      filtered = filtered.filter(img => img.provider === filterProvider);
    }

    // Apply sorting
    switch (sortBy) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        break;
      case 'predicted':
        // Sort by predicted preference (will be applied after predictions load)
        if (Object.keys(predictions).length > 0) {
          filtered.sort((a, b) => 
            (predictions[b.id]?.predicted_score || 0) - 
            (predictions[a.id]?.predicted_score || 0)
          );
        }
        break;
      default:
        break;
    }

    setFilteredImages(filtered);
  };

  const loadPredictions = async () => {
    setLoadingPredictions(true);
    const newPredictions = {};

    // Load predictions for first 20 images
    const imagesToPredict = filteredImages.slice(0, 20);
    
    for (const image of imagesToPredict) {
      try {
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/predict/${image.id}`
        );
        if (response.ok) {
          const prediction = await response.json();
          newPredictions[image.id] = prediction;
        }
      } catch (error) {
        console.error('Error loading prediction:', error);
      }
    }

    setPredictions(newPredictions);
    setLoadingPredictions(false);

    // Re-sort if sorting by predicted
    if (sortBy === 'predicted') {
      filterAndSortImages();
    }
  };

  const handleDownload = (image) => {
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = image.url;
    link.download = `${image.id}.png`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getPredictionColor = (score) => {
    if (score >= 0.7) return 'success';
    if (score >= 0.4) return 'warning';
    return 'error';
  };

  return (
    <Box>
      {/* Filters and Search */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search prompts..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ flexGrow: 1, minWidth: 300 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />

        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Sort By</InputLabel>
          <Select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            label="Sort By"
          >
            <MenuItem value="newest">Newest First</MenuItem>
            <MenuItem value="oldest">Oldest First</MenuItem>
            <MenuItem value="predicted">Predicted Preference</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Provider</InputLabel>
          <Select
            value={filterProvider}
            onChange={(e) => setFilterProvider(e.target.value)}
            label="Provider"
          >
            <MenuItem value="all">All Providers</MenuItem>
            <MenuItem value="openai">OpenAI</MenuItem>
            <MenuItem value="replicate">Replicate</MenuItem>
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          onClick={onRefresh}
          startIcon={<Refresh />}
        >
          Refresh
        </Button>
      </Box>

      {/* Loading predictions indicator */}
      {loadingPredictions && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Loading preference predictions...
          </Typography>
          <LinearProgress />
        </Box>
      )}

      {/* Results count */}
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Showing {filteredImages.length} of {images.length} images
      </Typography>

      {/* Image Grid */}
      <Grid container spacing={2}>
        {filteredImages.map((image) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={image.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardMedia
                component="img"
                height="250"
                image={image.url}
                alt={image.prompt}
                sx={{ cursor: 'pointer' }}
                onClick={() => setSelectedImage(image)}
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="body2" gutterBottom>
                  {image.prompt.length > 100
                    ? image.prompt.substring(0, 100) + '...'
                    : image.prompt}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={image.provider}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  {image.metadata?.style && (
                    <Chip
                      label={image.metadata.style}
                      size="small"
                      variant="outlined"
                    />
                  )}
                </Box>
                {predictions[image.id] && (
                  <Box sx={{ mt: 1 }}>
                    <Tooltip title={`Confidence: ${(predictions[image.id].confidence * 100).toFixed(0)}%`}>
                      <Chip
                        icon={<AutoAwesome />}
                        label={`${(predictions[image.id].predicted_score * 100).toFixed(0)}%`}
                        size="small"
                        color={getPredictionColor(predictions[image.id].predicted_score)}
                      />
                    </Tooltip>
                  </Box>
                )}
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                  {formatDate(image.created_at)}
                </Typography>
              </CardContent>
              <CardActions>
                <IconButton size="small" onClick={() => setSelectedImage(image)}>
                  <ZoomIn />
                </IconButton>
                <IconButton size="small" onClick={() => handleDownload(image)}>
                  <Download />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Image Detail Dialog */}
      <Dialog
        open={!!selectedImage}
        onClose={() => setSelectedImage(null)}
        maxWidth="lg"
        fullWidth
      >
        {selectedImage && (
          <>
            <DialogTitle>{selectedImage.prompt}</DialogTitle>
            <DialogContent>
              <Box sx={{ textAlign: 'center' }}>
                <img
                  src={selectedImage.url}
                  alt={selectedImage.prompt}
                  style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain' }}
                />
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Provider: {selectedImage.provider}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Created: {formatDate(selectedImage.created_at)}
                </Typography>
                {selectedImage.metadata?.style && (
                  <Typography variant="body2" color="text.secondary">
                    Style: {selectedImage.metadata.style}
                  </Typography>
                )}
                {selectedImage.metadata?.negative_prompt && (
                  <Typography variant="body2" color="text.secondary">
                    Negative prompt: {selectedImage.metadata.negative_prompt}
                  </Typography>
                )}
                {predictions[selectedImage.id] && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Predicted preference: {(predictions[selectedImage.id].predicted_score * 100).toFixed(0)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Confidence: {(predictions[selectedImage.id].confidence * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                )}
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => handleDownload(selectedImage)}>
                Download
              </Button>
              <Button onClick={() => setSelectedImage(null)}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}

export default Gallery;