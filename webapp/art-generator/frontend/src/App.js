import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
// WebSocket connection will be implemented directly

import ImageGenerator from './ImageGenerator';
import PreferenceUI from './PreferenceUI';
import Gallery from './Gallery';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [images, setImages] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Connect to WebSocket
    const wsUrl = `ws://localhost:8090/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Connected to backend WebSocket');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.status === 'completed' && data.image) {
        // Add new image to the list
        setImages(prev => [data.image, ...prev]);
      }
      
      if (data.type === 'preference_update') {
        // Handle preference updates
        console.log('Preference updated:', data);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setSocket(ws);

    // Load initial images
    fetchImages();

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const fetchImages = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8090'}/images`);
      const data = await response.json();
      setImages(data);
    } catch (error) {
      console.error('Error fetching images:', error);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleImageGenerated = (newImage) => {
    setImages(prev => [newImage, ...prev]);
  };

  const handlePreferenceUpdate = () => {
    // Refresh images to get updated scores
    fetchImages();
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Art Generator with Preference Learning
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ mt: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Generate" />
            <Tab label="Compare & Learn" />
            <Tab label="Gallery" />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <ImageGenerator 
            onImageGenerated={handleImageGenerated}
            images={images}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <PreferenceUI 
            images={images}
            onPreferenceUpdate={handlePreferenceUpdate}
            onGenerateOptimal={(taskId) => {
              // Switch to generate tab to see the new image
              setActiveTab(0);
            }}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Gallery 
            images={images}
            onRefresh={fetchImages}
          />
        </TabPanel>
      </Container>
    </ThemeProvider>
  );
}

export default App;