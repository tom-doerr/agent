import React, { useState } from 'react';
import './AudioRecorder.css';

function FileUploadAudio({ onTranscription, model = 'gemini-flash' }) {
  const [uploading, setUploading] = useState(false);
  const [audioFile, setAudioFile] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setAudioFile(file);
    setError(null);
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('audio', file);

      const response = await fetch(`http://localhost:8000/transcribe?model=${model}`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        onTranscription(data.text);
      } else {
        setError('Transcription failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setError(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="audio-uploader">
      <h4>Alternative: Upload Audio File</h4>
      <p style={{ fontSize: '12px', color: '#999' }}>
        Since browser microphone access requires PulseAudio, you can upload an audio file instead.
      </p>
      
      <input
        type="file"
        accept="audio/*,.webm,.mp3,.wav,.m4a"
        onChange={handleFileUpload}
        disabled={uploading}
        id="audio-file-input"
        style={{ display: 'none' }}
      />
      
      <label 
        htmlFor="audio-file-input" 
        className="upload-button"
        style={{
          display: 'inline-block',
          padding: '10px 20px',
          backgroundColor: '#4CAF50',
          color: 'white',
          borderRadius: '5px',
          cursor: uploading ? 'not-allowed' : 'pointer',
          opacity: uploading ? 0.5 : 1,
          marginTop: '10px'
        }}
      >
        {uploading ? 'Uploading...' : '📁 Choose Audio File'}
      </label>

      {audioFile && (
        <p style={{ fontSize: '12px', marginTop: '10px' }}>
          Selected: {audioFile.name}
        </p>
      )}

      {error && (
        <p className="error" style={{ fontSize: '12px', marginTop: '10px' }}>
          {error}
        </p>
      )}

      <div style={{ marginTop: '20px', fontSize: '11px', color: '#666' }}>
        <strong>To record audio on Linux without PulseAudio:</strong>
        <pre style={{ 
          backgroundColor: '#f0f0f0', 
          padding: '10px', 
          borderRadius: '5px',
          fontFamily: 'monospace',
          fontSize: '10px'
        }}>
{`# Record 10 seconds of audio:
arecord -d 10 -f cd -t wav output.wav

# Record from specific device:
arecord -D hw:1,0 -d 10 -f cd output.wav

# Convert to smaller format:
ffmpeg -i output.wav output.webm`}
        </pre>
      </div>
    </div>
  );
}

export default FileUploadAudio;