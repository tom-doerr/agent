import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Paper
} from '@mui/material';
import { AutoAwesome, Refresh } from '@mui/icons-material';

function ImageGenerator({ onImageGenerated, images }) {
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [provider, setProvider] = useState('openai');
  const [size, setSize] = useState('1024x1024');
  const [style, setStyle] = useState('');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [taskId, setTaskId] = useState(null);

  const styles = [
    { value: '', label: 'None' },
    { value: 'realistic', label: 'Realistic' },
    { value: 'anime', label: 'Anime' },
    { value: 'oil painting', label: 'Oil Painting' },
    { value: 'watercolor', label: 'Watercolor' },
    { value: 'digital art', label: 'Digital Art' },
    { value: 'pencil sketch', label: 'Pencil Sketch' },
    { value: '3d render', label: '3D Render' },
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setGenerating(true);
    setError(null);
    setGeneratedImage(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          negative_prompt: negativePrompt || null,
          provider,
          size,
          style: style || null,
        }),
      });

      const data = await response.json();
      setTaskId(data.task_id);

      // Poll for completion
      pollForCompletion(data.task_id);
    } catch (error) {
      setError(`Error generating image: ${error.message}`);
      setGenerating(false);
    }
  };

  const pollForCompletion = async (taskId) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/status/${taskId}`);
        const status = await response.json();

        if (status.status === 'completed') {
          clearInterval(interval);
          setGenerating(false);
          setGeneratedImage(status.result);
          onImageGenerated(status.result);
        } else if (status.status === 'failed') {
          clearInterval(interval);
          setGenerating(false);
          setError(status.error || 'Generation failed');
        }
      } catch (error) {
        clearInterval(interval);
        setGenerating(false);
        setError(`Error checking status: ${error.message}`);
      }
    }, 1000);
  };

  const handleGenerateOptimal = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/generate/optimal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          base_prompt: prompt || null,
        }),
      });

      const data = await response.json();
      setTaskId(data.task_id);
      pollForCompletion(data.task_id);
    } catch (error) {
      setError(`Error generating optimal image: ${error.message}`);
      setGenerating(false);
    }
  };

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Image Generation
            </Typography>

            <TextField
              fullWidth
              label="Prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              multiline
              rows={3}
              margin="normal"
              placeholder="Describe the image you want to generate..."
            />

            <TextField
              fullWidth
              label="Negative Prompt (optional)"
              value={negativePrompt}
              onChange={(e) => setNegativePrompt(e.target.value)}
              multiline
              rows={2}
              margin="normal"
              placeholder="What to avoid in the image..."
              disabled={provider === 'openai'}
            />

            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={4}>
                <FormControl fullWidth>
                  <InputLabel>Provider</InputLabel>
                  <Select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    label="Provider"
                  >
                    <MenuItem value="openai">OpenAI DALL-E</MenuItem>
                    <MenuItem value="replicate">Stable Diffusion</MenuItem>
                    <MenuItem value="local">Local Model</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={4}>
                <FormControl fullWidth>
                  <InputLabel>Size</InputLabel>
                  <Select
                    value={size}
                    onChange={(e) => setSize(e.target.value)}
                    label="Size"
                  >
                    <MenuItem value="512x512">512x512</MenuItem>
                    <MenuItem value="1024x1024">1024x1024</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={4}>
                <FormControl fullWidth>
                  <InputLabel>Style</InputLabel>
                  <Select
                    value={style}
                    onChange={(e) => setStyle(e.target.value)}
                    label="Style"
                  >
                    {styles.map((s) => (
                      <MenuItem key={s.value} value={s.value}>
                        {s.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={handleGenerate}
                disabled={generating}
                startIcon={generating ? <CircularProgress size={20} /> : <Refresh />}
              >
                {generating ? 'Generating...' : 'Generate'}
              </Button>

              <Button
                variant="outlined"
                onClick={handleGenerateOptimal}
                disabled={generating || images.length < 5}
                startIcon={<AutoAwesome />}
              >
                Generate Optimal
              </Button>
            </Box>

            {images.length < 5 && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Generate at least 5 images to use the "Generate Optimal" feature
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          {generatedImage && (
            <Card>
              <CardMedia
                component="img"
                image={generatedImage.url}
                alt={generatedImage.prompt}
                sx={{ maxHeight: 500 }}
              />
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  {generatedImage.prompt}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip label={generatedImage.provider} size="small" />
                  {generatedImage.metadata.style && (
                    <Chip label={generatedImage.metadata.style} size="small" sx={{ ml: 1 }} />
                  )}
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Recent Generations
        </Typography>
        <Grid container spacing={2}>
          {images.slice(0, 6).map((image) => (
            <Grid item xs={6} sm={4} md={3} key={image.id}>
              <Card>
                <CardMedia
                  component="img"
                  height="200"
                  image={image.url}
                  alt={image.prompt}
                />
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
}

export default ImageGenerator;