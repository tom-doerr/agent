import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PreferenceUI from '../PreferenceUI';

// Mock react-beautiful-dnd
jest.mock('react-beautiful-dnd', () => ({
  DragDropContext: ({ children }) => children,
  Droppable: ({ children }) => children({
    draggableProps: {},
    innerRef: jest.fn(),
  }),
  Draggable: ({ children }) => children({
    draggableProps: {},
    dragHandleProps: {},
    innerRef: jest.fn(),
  }, {}),
}));

const mockImages = [
  {
    id: 'image1',
    url: 'http://example.com/image1.png',
    prompt: 'Test image 1',
    provider: 'openai',
    created_at: '2024-01-01T00:00:00',
  },
  {
    id: 'image2',
    url: 'http://example.com/image2.png',
    prompt: 'Test image 2',
    provider: 'replicate',
    created_at: '2024-01-01T00:00:00',
  },
  {
    id: 'image3',
    url: 'http://example.com/image3.png',
    prompt: 'Test image 3',
    provider: 'openai',
    created_at: '2024-01-01T00:00:00',
  },
];

describe('PreferenceUI Component', () => {
  const mockOnPreferenceUpdate = jest.fn();

  beforeEach(() => {
    mockOnPreferenceUpdate.mockClear();
    global.fetch = jest.fn();
  });

  test('renders all sections', () => {
    render(
      <PreferenceUI 
        images={mockImages} 
        onPreferenceUpdate={mockOnPreferenceUpdate} 
      />
    );
    
    expect(screen.getByText('A/B Comparison')).toBeInTheDocument();
    expect(screen.getByText('Rate Images')).toBeInTheDocument();
    expect(screen.getByText('Rank Your Favorites')).toBeInTheDocument();
  });

  test('starts comparison when button clicked', async () => {
    const user = userEvent.setup();
    render(
      <PreferenceUI 
        images={mockImages} 
        onPreferenceUpdate={mockOnPreferenceUpdate} 
      />
    );
    
    const startButton = screen.getByText('Start Comparison');
    await user.click(startButton);
    
    // Should show two images for comparison
    await waitFor(() => {
      const images = screen.getAllByRole('img');
      expect(images.length).toBeGreaterThanOrEqual(2);
    });
  });

  test('disables start comparison with less than 2 images', () => {
    render(
      <PreferenceUI 
        images={[mockImages[0]]} 
        onPreferenceUpdate={mockOnPreferenceUpdate} 
      />
    );
    
    const startButton = screen.getByText('Start Comparison');
    expect(startButton).toBeDisabled();
  });

  test('submits comparison preference', async () => {
    fetch.mockResolvedValueOnce({ ok: true });
    const user = userEvent.setup();
    
    render(
      <PreferenceUI 
        images={mockImages} 
        onPreferenceUpdate={mockOnPreferenceUpdate} 
      />
    );
    
    // Start comparison
    const startButton = screen.getByText('Start Comparison');
    await user.click(startButton);
    
    // Click on first image
    const images = screen.getAllByRole('img');
    await user.click(images[0]);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/preferences/compare'),
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        })
      );
    });
  });

  test('displays ranking section with draggable items', () => {
    render(
      <PreferenceUI 
        images={mockImages} 
        onPreferenceUpdate={mockOnPreferenceUpdate} 
      />
    );
    
    // Should show rankings
    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#2')).toBeInTheDocument();
  });

  test('shows success message after action', async () => {
    fetch.mockResolvedValueOnce({ ok: true });
    const user = userEvent.setup();
    
    render(
      <PreferenceUI 
        images={mockImages} 
        onPreferenceUpdate={mockOnPreferenceUpdate} 
      />
    );
    
    // Start comparison
    const startButton = screen.getByText('Start Comparison');
    await user.click(startButton);
    
    // Click on first image
    const images = screen.getAllByRole('img');
    await user.click(images[0]);
    
    // Should show success message
    await waitFor(() => {
      expect(screen.getByText('Preference recorded!')).toBeInTheDocument();
    });
  });
});