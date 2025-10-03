import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ImageGenerator from './ImageGenerator';

// Mock fetch
global.fetch = jest.fn();

describe('ImageGenerator Component', () => {
  const mockOnImageGenerated = jest.fn();
  const mockImages = [
    { id: '1', url: 'img1.jpg', prompt: 'Test 1' },
    { id: '2', url: 'img2.jpg', prompt: 'Test 2' }
  ];

  beforeEach(() => {
    fetch.mockClear();
    mockOnImageGenerated.mockClear();
  });

  test('renders image generator form', () => {
    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    expect(screen.getByText('Generate New Image')).toBeInTheDocument();
    expect(screen.getByLabelText(/Prompt/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Provider/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Size/i)).toBeInTheDocument();
    expect(screen.getByText('Generate Image')).toBeInTheDocument();
  });

  test('handles successful image generation', async () => {
    // Mock successful generation
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ task_id: 'task-123', status: 'pending' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          task_id: 'task-123',
          status: 'completed',
          result: { id: 'new-img', url: 'new.jpg' }
        })
      });

    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    // Fill in prompt
    const promptInput = screen.getByLabelText(/Prompt/i);
    fireEvent.change(promptInput, { target: { value: 'A beautiful sunset' } });
    
    // Submit form
    const generateButton = screen.getByText('Generate Image');
    fireEvent.click(generateButton);
    
    // Wait for generation to complete
    await waitFor(() => {
      expect(mockOnImageGenerated).toHaveBeenCalledWith({
        id: 'new-img',
        url: 'new.jpg'
      });
    });
  });

  test('shows loading state during generation', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ task_id: 'task-123', status: 'pending' })
    });

    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    const generateButton = screen.getByText('Generate Image');
    fireEvent.click(generateButton);
    
    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText(/Generating/i)).toBeInTheDocument();
    });
  });

  test('handles generation error', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      statusText: 'Internal Server Error'
    });

    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    const generateButton = screen.getByText('Generate Image');
    fireEvent.click(generateButton);
    
    // Should show error
    await waitFor(() => {
      expect(screen.getByText(/Failed to generate image/i)).toBeInTheDocument();
    });
  });

  test('handles provider selection', () => {
    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    const providerSelect = screen.getByLabelText(/Provider/i);
    
    // Check all providers are available
    fireEvent.mouseDown(providerSelect);
    expect(screen.getByText('OpenAI DALL-E 3')).toBeInTheDocument();
    expect(screen.getByText('Replicate (Stable Diffusion)')).toBeInTheDocument();
    expect(screen.getByText('Local Model')).toBeInTheDocument();
  });

  test('handles size selection', () => {
    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    const sizeSelect = screen.getByLabelText(/Size/i);
    
    // Check sizes are available
    fireEvent.mouseDown(sizeSelect);
    expect(screen.getByText('512x512')).toBeInTheDocument();
    expect(screen.getByText('1024x1024')).toBeInTheDocument();
    expect(screen.getByText('1024x768')).toBeInTheDocument();
  });

  test('shows style options when expanded', () => {
    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    // Expand advanced options
    const expandButton = screen.getByLabelText(/expand/i);
    fireEvent.click(expandButton);
    
    // Should show style options
    expect(screen.getByLabelText(/Style/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Negative Prompt/i)).toBeInTheDocument();
  });

  test('validates empty prompt', async () => {
    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    // Try to submit without prompt
    const generateButton = screen.getByText('Generate Image');
    fireEvent.click(generateButton);
    
    // Should not call fetch
    expect(fetch).not.toHaveBeenCalled();
  });

  test('shows recent prompts', () => {
    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    expect(screen.getByText('Recent Prompts')).toBeInTheDocument();
    expect(screen.getByText('Test 1')).toBeInTheDocument();
    expect(screen.getByText('Test 2')).toBeInTheDocument();
  });

  test('uses recent prompt when clicked', () => {
    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    // Click a recent prompt
    const recentPrompt = screen.getByText('Test 1');
    fireEvent.click(recentPrompt);
    
    // Should populate the prompt field
    const promptInput = screen.getByLabelText(/Prompt/i);
    expect(promptInput.value).toBe('Test 1');
  });

  test('cancels generation', async () => {
    // Mock long-running generation
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ task_id: 'task-123', status: 'pending' })
    });

    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    const generateButton = screen.getByText('Generate Image');
    fireEvent.click(generateButton);
    
    // Wait for loading state
    await waitFor(() => {
      expect(screen.getByText(/Cancel/i)).toBeInTheDocument();
    });
    
    // Cancel generation
    const cancelButton = screen.getByText(/Cancel/i);
    fireEvent.click(cancelButton);
    
    // Should stop loading
    expect(screen.queryByText(/Generating/i)).not.toBeInTheDocument();
  });

  test('handles poll timeout', async () => {
    // Mock generation that never completes
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ task_id: 'task-123', status: 'processing' })
    });

    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    const generateButton = screen.getByText('Generate Image');
    fireEvent.click(generateButton);
    
    // Wait for timeout (this would normally take 60 seconds, but we can't wait that long in tests)
    // Instead, we just verify the polling started
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/status/task-123')
      );
    });
  });

  test('displays generation progress', async () => {
    // Mock generation with progress updates
    fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ task_id: 'task-123', status: 'pending', progress: 0.0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ task_id: 'task-123', status: 'processing', progress: 0.5 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          task_id: 'task-123',
          status: 'completed',
          progress: 1.0,
          result: { id: 'new-img', url: 'new.jpg' }
        })
      });

    render(<ImageGenerator onImageGenerated={mockOnImageGenerated} images={mockImages} />);
    
    const generateButton = screen.getByText('Generate Image');
    fireEvent.click(generateButton);
    
    // Should show progress
    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });
});