import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock child components
jest.mock('./ImageGenerator', () => {
  return function ImageGenerator({ onImageGenerated }) {
    return (
      <div data-testid="image-generator">
        <button onClick={() => onImageGenerated({ id: 'test-id', url: 'test.jpg' })}>
          Generate Image
        </button>
      </div>
    );
  };
});

jest.mock('./PreferenceUI', () => {
  return function PreferenceUI({ images, onPreferenceUpdate, onGenerateOptimal }) {
    return (
      <div data-testid="preference-ui">
        <button onClick={onPreferenceUpdate}>Update Preferences</button>
        <button onClick={() => onGenerateOptimal('task-123')}>Generate Optimal</button>
      </div>
    );
  };
});

jest.mock('./Gallery', () => {
  return function Gallery({ images, onRefresh }) {
    return (
      <div data-testid="gallery">
        <button onClick={onRefresh}>Refresh Gallery</button>
        <div>{images.length} images</div>
      </div>
    );
  };
});

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.OPEN;
    setTimeout(() => {
      if (this.onopen) this.onopen();
    }, 0);
  }
  
  close() {
    this.readyState = WebSocket.CLOSED;
  }
  
  send(data) {
    // Mock send
  }
}

global.WebSocket = MockWebSocket;

// Mock fetch
global.fetch = jest.fn();

describe('App Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    fetch.mockResolvedValue({
      ok: true,
      json: async () => []
    });
  });

  test('renders app with all tabs', () => {
    render(<App />);
    
    expect(screen.getByText('AI Art Generator with Preference Learning')).toBeInTheDocument();
    expect(screen.getByText('Generate')).toBeInTheDocument();
    expect(screen.getByText('Compare & Learn')).toBeInTheDocument();
    expect(screen.getByText('Gallery')).toBeInTheDocument();
  });

  test('switches between tabs', () => {
    render(<App />);
    
    // Initially on Generate tab
    expect(screen.getByTestId('image-generator')).toBeInTheDocument();
    
    // Switch to Compare & Learn
    fireEvent.click(screen.getByText('Compare & Learn'));
    expect(screen.getByTestId('preference-ui')).toBeInTheDocument();
    
    // Switch to Gallery
    fireEvent.click(screen.getByText('Gallery'));
    expect(screen.getByTestId('gallery')).toBeInTheDocument();
  });

  test('handles image generation', async () => {
    render(<App />);
    
    // Generate an image
    const generateButton = screen.getByText('Generate Image');
    fireEvent.click(generateButton);
    
    // Switch to gallery to see the image
    fireEvent.click(screen.getByText('Gallery'));
    
    await waitFor(() => {
      expect(screen.getByText('1 images')).toBeInTheDocument();
    });
  });

  test('handles preference update', async () => {
    render(<App />);
    
    // Mock fetch for image refresh
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [
        { id: '1', url: 'img1.jpg', score: 0.8 },
        { id: '2', url: 'img2.jpg', score: 0.6 }
      ]
    });
    
    // Switch to preferences tab
    fireEvent.click(screen.getByText('Compare & Learn'));
    
    // Update preferences
    const updateButton = screen.getByText('Update Preferences');
    fireEvent.click(updateButton);
    
    // Verify fetch was called
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/images')
      );
    });
  });

  test('handles optimal generation and tab switch', () => {
    render(<App />);
    
    // Switch to preferences tab
    fireEvent.click(screen.getByText('Compare & Learn'));
    
    // Generate optimal image
    const generateOptimalButton = screen.getByText('Generate Optimal');
    fireEvent.click(generateOptimalButton);
    
    // Should switch back to Generate tab
    expect(screen.getByTestId('image-generator')).toBeInTheDocument();
  });

  test('loads initial images on mount', async () => {
    const mockImages = [
      { id: '1', url: 'img1.jpg' },
      { id: '2', url: 'img2.jpg' }
    ];
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockImages
    });
    
    render(<App />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/images')
      );
    });
  });

  test('handles WebSocket connection', () => {
    const mockWebSocket = jest.fn();
    global.WebSocket = mockWebSocket;
    
    render(<App />);
    
    expect(mockWebSocket).toHaveBeenCalledWith('ws://localhost:8090/ws');
  });

  test('handles WebSocket messages', async () => {
    let wsInstance;
    global.WebSocket = class extends MockWebSocket {
      constructor(url) {
        super(url);
        wsInstance = this;
      }
    };
    
    render(<App />);
    
    // Simulate receiving a completed image
    await waitFor(() => {
      if (wsInstance && wsInstance.onmessage) {
        wsInstance.onmessage({
          data: JSON.stringify({
            status: 'completed',
            image: { id: 'new-img', url: 'new.jpg' }
          })
        });
      }
    });
    
    // Check gallery for new image
    fireEvent.click(screen.getByText('Gallery'));
    await waitFor(() => {
      expect(screen.getByText('1 images')).toBeInTheDocument();
    });
  });

  test('handles WebSocket error', () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation();
    let wsInstance;
    
    global.WebSocket = class extends MockWebSocket {
      constructor(url) {
        super(url);
        wsInstance = this;
      }
    };
    
    render(<App />);
    
    // Simulate WebSocket error
    if (wsInstance && wsInstance.onerror) {
      wsInstance.onerror(new Error('Connection failed'));
    }
    
    expect(consoleError).toHaveBeenCalledWith(
      'WebSocket error:',
      expect.any(Error)
    );
    
    consoleError.mockRestore();
  });

  test('cleans up WebSocket on unmount', () => {
    let wsInstance;
    global.WebSocket = class extends MockWebSocket {
      constructor(url) {
        super(url);
        wsInstance = this;
        this.close = jest.fn();
      }
    };
    
    const { unmount } = render(<App />);
    
    unmount();
    
    expect(wsInstance.close).toHaveBeenCalled();
  });
});