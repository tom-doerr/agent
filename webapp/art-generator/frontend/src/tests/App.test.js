import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';

// Mock socket.io
jest.mock('socket.io-client', () => {
  const emit = jest.fn();
  const on = jest.fn();
  const close = jest.fn();
  
  return jest.fn(() => ({
    emit,
    on,
    close,
  }));
});

// Mock fetch
global.fetch = jest.fn();

describe('App Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    fetch.mockResolvedValue({
      ok: true,
      json: async () => [],
    });
  });

  test('renders app with title', () => {
    render(<App />);
    const titleElement = screen.getByText(/AI Art Generator with Preference Learning/i);
    expect(titleElement).toBeInTheDocument();
  });

  test('renders all tabs', () => {
    render(<App />);
    expect(screen.getByText('Generate')).toBeInTheDocument();
    expect(screen.getByText('Compare & Learn')).toBeInTheDocument();
    expect(screen.getByText('Gallery')).toBeInTheDocument();
  });

  test('switches between tabs', async () => {
    const user = userEvent.setup();
    render(<App />);
    
    // Click on Compare & Learn tab
    const compareTab = screen.getByText('Compare & Learn');
    await user.click(compareTab);
    
    // Click on Gallery tab
    const galleryTab = screen.getByText('Gallery');
    await user.click(galleryTab);
  });

  test('fetches images on mount', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/images')
      );
    });
  });
});