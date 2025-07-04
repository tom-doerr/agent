import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

// Mock EventSource
global.EventSource = jest.fn(() => ({
  addEventListener: jest.fn(),
  close: jest.fn(),
}));

describe('App Component', () => {
  beforeEach(() => {
    global.EventSource.mockClear();
  });

  test('renders heading', () => {
    render(<App />);
    const heading = screen.getByText(/DSPy Streaming Demo/i);
    expect(heading).toBeInTheDocument();
  });

  test('renders input and button', () => {
    render(<App />);
    const input = screen.getByTestId('question-input');
    const button = screen.getByTestId('submit-button');
    
    expect(input).toBeInTheDocument();
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Ask');
  });

  test('button is disabled when input is empty', () => {
    render(<App />);
    const button = screen.getByTestId('submit-button');
    expect(button).toBeDisabled();
  });

  test('button is enabled when input has text', async () => {
    render(<App />);
    const input = screen.getByTestId('question-input');
    const button = screen.getByTestId('submit-button');
    
    await userEvent.type(input, 'Test question');
    expect(button).not.toBeDisabled();
  });

  test('submitting form starts streaming', async () => {
    const mockEventSource = {
      onmessage: null,
      onerror: null,
      close: jest.fn(),
    };
    global.EventSource.mockReturnValue(mockEventSource);

    render(<App />);
    const input = screen.getByTestId('question-input');
    const button = screen.getByTestId('submit-button');
    
    await userEvent.type(input, 'What is React?');
    fireEvent.click(button);

    expect(button).toHaveTextContent('Streaming...');
    expect(button).toBeDisabled();
    expect(global.EventSource).toHaveBeenCalledWith(
      'http://localhost:8000/stream/What%20is%20React%3F'
    );
  });

  test('displays streamed response', async () => {
    const mockEventSource = {
      onmessage: null,
      onerror: null,
      close: jest.fn(),
    };
    global.EventSource.mockReturnValue(mockEventSource);

    render(<App />);
    const input = screen.getByTestId('question-input');
    const button = screen.getByTestId('submit-button');
    
    await userEvent.type(input, 'Test question');
    fireEvent.click(button);

    // Simulate streaming response
    mockEventSource.onmessage({ data: JSON.stringify({ chunk: 'React ' }) });
    mockEventSource.onmessage({ data: JSON.stringify({ chunk: 'is ' }) });
    mockEventSource.onmessage({ data: JSON.stringify({ chunk: 'awesome!' }) });
    mockEventSource.onmessage({ data: JSON.stringify({ done: true }) });

    await waitFor(() => {
      const response = screen.getByTestId('response');
      expect(response).toHaveTextContent('React is awesome!');
    });

    expect(button).toHaveTextContent('Ask');
    expect(button).not.toBeDisabled();
  });

  test('displays error on connection failure', async () => {
    const mockEventSource = {
      onmessage: null,
      onerror: null,
      close: jest.fn(),
    };
    global.EventSource.mockReturnValue(mockEventSource);

    render(<App />);
    const input = screen.getByTestId('question-input');
    const button = screen.getByTestId('submit-button');
    
    await userEvent.type(input, 'Test question');
    fireEvent.click(button);

    // Simulate error
    mockEventSource.onerror({});

    await waitFor(() => {
      const error = screen.getByTestId('error-message');
      expect(error).toHaveTextContent('Connection error');
    });
  });
});