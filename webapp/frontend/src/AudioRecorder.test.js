import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AudioRecorder from './AudioRecorder';

// Mock the MediaRecorder API
const mockMediaRecorder = {
  start: jest.fn(),
  stop: jest.fn(),
  ondataavailable: null,
  onstop: null,
};

const mockGetUserMedia = jest.fn();

global.navigator.mediaDevices = {
  getUserMedia: mockGetUserMedia,
};

global.MediaRecorder = jest.fn(() => mockMediaRecorder);
global.URL.createObjectURL = jest.fn();
global.Blob = jest.fn();

// Mock fetch
global.fetch = jest.fn();

describe('AudioRecorder', () => {
  const mockOnTranscription = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockGetUserMedia.mockResolvedValue({
      getTracks: () => [{ stop: jest.fn() }],
    });
  });

  test('renders record button', () => {
    render(<AudioRecorder onTranscription={mockOnTranscription} />);
    const button = screen.getByTestId('record-button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('🎤 Start Recording');
  });

  test('starts recording when button clicked', async () => {
    render(<AudioRecorder onTranscription={mockOnTranscription} />);
    const button = screen.getByTestId('record-button');
    
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
      expect(mockMediaRecorder.start).toHaveBeenCalled();
      expect(button).toHaveTextContent('🛑 Stop Recording');
    });
  });

  test('stops recording when stop button clicked', async () => {
    render(<AudioRecorder onTranscription={mockOnTranscription} />);
    const button = screen.getByTestId('record-button');
    
    // Start recording
    fireEvent.click(button);
    await waitFor(() => expect(button).toHaveTextContent('🛑 Stop Recording'));
    
    // Stop recording
    fireEvent.click(button);
    
    expect(mockMediaRecorder.stop).toHaveBeenCalled();
  });

  test('handles transcription after recording stops', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ text: 'Transcribed text' }),
    });

    render(<AudioRecorder onTranscription={mockOnTranscription} />);
    const button = screen.getByTestId('record-button');
    
    // Start recording
    fireEvent.click(button);
    await waitFor(() => expect(mockMediaRecorder.start).toHaveBeenCalled());
    
    // Simulate data available
    const mockData = new Blob(['audio data'], { type: 'audio/webm' });
    mockMediaRecorder.ondataavailable({ data: mockData });
    
    // Stop recording and trigger onstop
    fireEvent.click(button);
    await mockMediaRecorder.onstop();
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/transcribe', {
        method: 'POST',
        body: expect.any(FormData),
      });
      expect(mockOnTranscription).toHaveBeenCalledWith('Transcribed text');
    });
  });

  test('handles microphone permission error', async () => {
    mockGetUserMedia.mockRejectedValueOnce(new Error('Permission denied'));
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    render(<AudioRecorder onTranscription={mockOnTranscription} />);
    const button = screen.getByTestId('record-button');
    
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalledWith('Could not access microphone. Please check permissions.');
    });
    
    alertSpy.mockRestore();
  });

  test('handles transcription error gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<AudioRecorder onTranscription={mockOnTranscription} />);
    const button = screen.getByTestId('record-button');
    
    // Start and stop recording
    fireEvent.click(button);
    await waitFor(() => expect(mockMediaRecorder.start).toHaveBeenCalled());
    
    const mockData = new Blob(['audio data'], { type: 'audio/webm' });
    mockMediaRecorder.ondataavailable({ data: mockData });
    
    fireEvent.click(button);
    await mockMediaRecorder.onstop();
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Transcription error:', expect.any(Error));
    });
    
    consoleSpy.mockRestore();
  });
});