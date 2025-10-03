import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import '@testing-library/jest-dom';
import PreferenceUI from './PreferenceUI';

// Mock fetch
global.fetch = jest.fn();

// Mock react-beautiful-dnd
jest.mock('react-beautiful-dnd', () => ({
  DragDropContext: ({ children, onDragEnd }) => {
    return <div data-testid="drag-context" onClick={() => onDragEnd({ destination: { index: 1 }, source: { index: 0 } })}>{children}</div>;
  },
  Droppable: ({ children }) => children({
    droppableProps: {},
    innerRef: jest.fn(),
    placeholder: null
  }),
  Draggable: ({ children, index }) => children({
    draggableProps: { 'data-index': index },
    dragHandleProps: {},
    innerRef: jest.fn()
  }, { isDragging: false })
}));

describe('PreferenceUI Component', () => {
  const mockOnPreferenceUpdate = jest.fn();
  const mockOnGenerateOptimal = jest.fn();
  const mockImages = [
    { id: '1', url: 'img1.jpg', prompt: 'Test 1', provider: 'openai' },
    { id: '2', url: 'img2.jpg', prompt: 'Test 2', provider: 'replicate' },
    { id: '3', url: 'img3.jpg', prompt: 'Test 3', provider: 'local' },
    { id: '4', url: 'img4.jpg', prompt: 'Test 4', provider: 'openai' }
  ];

  beforeEach(() => {
    fetch.mockClear();
    mockOnPreferenceUpdate.mockClear();
    mockOnGenerateOptimal.mockClear();
  });

  test('renders all preference sections', () => {
    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    expect(screen.getByText('Generate Image Based on My Preferences')).toBeInTheDocument();
    expect(screen.getByText('A/B Comparison')).toBeInTheDocument();
    expect(screen.getByText('Rate Images')).toBeInTheDocument();
    expect(screen.getByText('Rank Your Favorites')).toBeInTheDocument();
  });

  test('shows generate optimal button enabled with enough images', () => {
    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    const generateButton = screen.getByText('Generate Image Based on My Preferences');
    expect(generateButton).not.toBeDisabled();
  });

  test('shows generate optimal button disabled with few images', () => {
    render(
      <PreferenceUI 
        images={[mockImages[0], mockImages[1]]}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    const generateButton = screen.getByText('Generate Image Based on My Preferences');
    expect(generateButton).toBeDisabled();
    expect(screen.getByText(/Rate or compare at least 3 images/)).toBeInTheDocument();
  });

  test('handles optimal image generation', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ task_id: 'optimal-task-123' })
    });

    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    const generateButton = screen.getByText('Generate Image Based on My Preferences');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/generate/optimal'),
        expect.objectContaining({ method: 'POST' })
      );
      expect(mockOnGenerateOptimal).toHaveBeenCalledWith('optimal-task-123');
    });
  });

  test('starts A/B comparison', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ image1_id: '1', image2_id: '2' })
    });

    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    const startButton = screen.getByText('Start Comparison');
    fireEvent.click(startButton);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/preferences/suggest-comparison')
      );
    });
  });

  test('handles A/B comparison selection', async () => {
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ image1_id: '1', image2_id: '2' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'success' })
      });

    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    // Start comparison
    fireEvent.click(screen.getByText('Start Comparison'));
    
    // Wait for images to load
    await waitFor(() => {
      expect(screen.getAllByRole('img')).toHaveLength(2);
    });
    
    // Click first image (winner)
    const firstImage = screen.getAllByRole('img')[0];
    fireEvent.click(firstImage.parentElement.parentElement);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/preferences/compare'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('winner_id')
        })
      );
      expect(mockOnPreferenceUpdate).toHaveBeenCalled();
    });
  });

  test('handles image rating', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success' })
    });

    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    // Click an image to rate
    const rateSection = screen.getByText('Rate Images').parentElement;
    const imageToRate = rateSection.querySelector('img');
    fireEvent.click(imageToRate.parentElement.parentElement);
    
    // Should show rating slider
    await waitFor(() => {
      expect(screen.getByText(/Rating:/)).toBeInTheDocument();
    });
    
    // Submit rating
    const submitButton = screen.getByText('Submit Rating');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/preferences/rate'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('score')
        })
      );
      expect(mockOnPreferenceUpdate).toHaveBeenCalled();
    });
  });

  test('handles rating slider change', async () => {
    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    // Select an image
    const rateSection = screen.getByText('Rate Images').parentElement;
    const imageToRate = rateSection.querySelector('img');
    fireEvent.click(imageToRate.parentElement.parentElement);
    
    // Find slider
    const slider = screen.getByRole('slider');
    
    // Change value
    fireEvent.change(slider, { target: { value: 0.8 } });
    
    // Check value updated
    expect(screen.getByText('Rating: 0.80')).toBeInTheDocument();
  });

  test('cancels rating', async () => {
    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    // Select an image
    const rateSection = screen.getByText('Rate Images').parentElement;
    const imageToRate = rateSection.querySelector('img');
    fireEvent.click(imageToRate.parentElement.parentElement);
    
    // Cancel
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    // Should go back to image grid
    await waitFor(() => {
      expect(screen.queryByText(/Rating:/)).not.toBeInTheDocument();
    });
  });

  test('shows drag and drop ranking', () => {
    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    // Check ranking section
    const rankSection = screen.getByText('Rank Your Favorites').parentElement;
    expect(rankSection).toBeInTheDocument();
    
    // Should show images in ranking
    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#2')).toBeInTheDocument();
  });

  test('handles drag and drop reordering', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success' })
    });

    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    // Simulate drag end
    const dragContext = screen.getByTestId('drag-context');
    fireEvent.click(dragContext);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/preferences/rank'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('image_rankings')
        })
      );
      expect(mockOnPreferenceUpdate).toHaveBeenCalled();
    });
  });

  test('shows empty state for rankings', () => {
    render(
      <PreferenceUI 
        images={[]}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    expect(screen.getByText('No images available for ranking. Generate some images first!')).toBeInTheDocument();
  });

  test('shows success messages', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success' })
    });

    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    // Submit a rating
    const rateSection = screen.getByText('Rate Images').parentElement;
    const imageToRate = rateSection.querySelector('img');
    fireEvent.click(imageToRate.parentElement.parentElement);
    
    const submitButton = screen.getByText('Submit Rating');
    fireEvent.click(submitButton);
    
    // Should show success message
    await waitFor(() => {
      expect(screen.getByText('Rating submitted!')).toBeInTheDocument();
    });
    
    // Message should disappear after timeout
    await waitFor(() => {
      expect(screen.queryByText('Rating submitted!')).not.toBeInTheDocument();
    }, { timeout: 3000 });
  });

  test('handles API errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));
    const consoleError = jest.spyOn(console, 'error').mockImplementation();

    render(
      <PreferenceUI 
        images={mockImages}
        onPreferenceUpdate={mockOnPreferenceUpdate}
        onGenerateOptimal={mockOnGenerateOptimal}
      />
    );
    
    const generateButton = screen.getByText('Generate Image Based on My Preferences');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(consoleError).toHaveBeenCalled();
    });
    
    consoleError.mockRestore();
  });
});