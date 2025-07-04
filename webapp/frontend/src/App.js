import React, { useState, useEffect } from 'react';
import AudioRecorder from './AudioRecorder';
import LiveAudioRecorder from './LiveAudioRecorder';
import FileUploadAudio from './FileUploadAudio';
import './App.css';

function App() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState('');
  const [textModel, setTextModel] = useState('gemini-flash');
  const [audioModel, setAudioModel] = useState('gemini-flash');
  const [config, setConfig] = useState(null);
  const [stats, setStats] = useState({
    tokens: 0,
    tokensPerSec: 0,
    totalTime: 0,
    model: ''
  });

  useEffect(() => {
    // Fetch configuration on mount
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => {
        setConfig(data);
        if (data.text_models && data.text_models.length > 0) {
          setTextModel(data.text_models[0]);
        }
        if (data.audio_models && data.audio_models.length > 0) {
          setAudioModel(data.audio_models[0]);
        }
      })
      .catch(err => console.error('Failed to fetch config:', err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setResponse('');
    setError('');
    setIsStreaming(true);
    setStats({ tokens: 0, tokensPerSec: 0, totalTime: 0, model: textModel });

    try {
      const eventSource = new EventSource(
        `http://localhost:8000/stream/${encodeURIComponent(question)}?model=${textModel}`
      );
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.chunk) {
          setResponse(prev => prev + data.chunk);
          if (data.tokens !== undefined) {
            setStats(prev => ({
              ...prev,
              tokens: data.tokens,
              tokensPerSec: data.tokens_per_sec || 0
            }));
          }
        } else if (data.done) {
          if (data.total_tokens !== undefined) {
            setStats(prev => ({
              ...prev,
              tokens: data.total_tokens,
              totalTime: data.total_time || 0,
              tokensPerSec: data.avg_tokens_per_sec || 0
            }));
          }
          eventSource.close();
          setIsStreaming(false);
        } else if (data.error) {
          setError(data.error);
          eventSource.close();
          setIsStreaming(false);
        } else if (data.start && data.model) {
          setStats(prev => ({ ...prev, model: data.model }));
        }
      };

      eventSource.onerror = (err) => {
        setError('Connection error');
        eventSource.close();
        setIsStreaming(false);
      };
    } catch (err) {
      setError(err.message);
      setIsStreaming(false);
    }
  };

  const handleAudioData = async (audioData) => {
    // Send audio directly to the model as multimodal input
    setResponse('');
    setError('');
    setIsStreaming(true);
    setStats({ tokens: 0, tokensPerSec: 0, totalTime: 0, model: audioModel });

    try {
      // Show that we're processing audio
      setQuestion(`[Audio Input: ${audioData.deviceLabel} - ${(audioData.blob.size / 1024).toFixed(1)}KB]`);
      
      // Send audio to the audio streaming endpoint
      const formData = new FormData();
      formData.append('audio', audioData.blob, 'recording.webm');
      
      const response = await fetch(`http://localhost:8000/audio-stream?model=${audioModel}`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.chunk) {
                setResponse(prev => prev + data.chunk);
              } else if (data.done) {
                setIsStreaming(false);
              } else if (data.error) {
                setError(data.error);
                setIsStreaming(false);
              } else if (data.start && data.model) {
                setStats(prev => ({ ...prev, model: data.model }));
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
      setIsStreaming(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>DSPy Streaming Demo</h1>
        
        {config && (
          <div className="config-info">
            <h3>Configuration</h3>
            <p>Mode: {config.config.mock_mode ? 'Mock' : 'Live'}</p>
            <p>Available endpoints: {config.config.available_endpoints.join(', ')}</p>
          </div>
        )}
        
        <div className="model-selectors">
          <div className="selector-group">
            <label htmlFor="text-model">Text Model:</label>
            <select 
              id="text-model"
              value={textModel} 
              onChange={(e) => setTextModel(e.target.value)}
              disabled={isStreaming}
              className="model-selector"
              data-testid="text-model-selector"
            >
              {config?.text_models?.map(model => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div>
          
          <div className="selector-group">
            <label htmlFor="audio-model">Audio Model:</label>
            <select 
              id="audio-model"
              value={audioModel} 
              onChange={(e) => setAudioModel(e.target.value)}
              disabled={isStreaming}
              className="model-selector"
              data-testid="audio-model-selector"
            >
              {config?.audio_models?.map(model => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="audio-section">
          <AudioRecorder 
            onAudioData={handleAudioData} 
            model={audioModel}
          />
          
          <div style={{ marginTop: '40px', borderTop: '2px solid #61dafb', paddingTop: '20px' }}>
            <LiveAudioRecorder 
              model={audioModel}
              onStatusChange={(status) => console.log('Live streaming status:', status)}
            />
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="question-form">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            disabled={isStreaming}
            className="question-input"
            data-testid="question-input"
          />
          <button 
            type="submit" 
            disabled={isStreaming || !question.trim()}
            className="submit-button"
            data-testid="submit-button"
          >
            {isStreaming ? 'Streaming...' : 'Ask'}
          </button>
        </form>

        {isStreaming && stats.tokens > 0 && (
          <div className="stats" data-testid="streaming-stats">
            <h4>Streaming Stats</h4>
            <p>Model: {stats.model}</p>
            <p>Tokens: {stats.tokens}</p>
            <p>Speed: {stats.tokensPerSec} tokens/s</p>
          </div>
        )}

        {!isStreaming && stats.totalTime > 0 && (
          <div className="stats" data-testid="final-stats">
            <h4>Final Stats</h4>
            <p>Model: {stats.model}</p>
            <p>Total tokens: {stats.tokens}</p>
            <p>Total time: {stats.totalTime}s</p>
            <p>Average speed: {stats.tokensPerSec} tokens/s</p>
          </div>
        )}

        {error && (
          <div className="error" data-testid="error-message">
            Error: {error}
          </div>
        )}

        {response && (
          <div className="response" data-testid="response">
            <h3>Response:</h3>
            <p>{response}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;