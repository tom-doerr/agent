import React, { useState, useRef, useEffect } from 'react';
import './AudioDebugger.css';

function AudioDebugger() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('default');
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    // Get audio devices
    const getDevices = async () => {
      try {
        const deviceList = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = deviceList.filter(d => d.kind === 'audioinput');
        setDevices(audioInputs);
        addLog(`Found ${audioInputs.length} audio input devices`);
      } catch (err) {
        addLog(`Error getting devices: ${err.message}`, 'error');
      }
    };
    
    getDevices();
    
    // Listen for device changes
    navigator.mediaDevices.ondevicechange = getDevices;
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }].slice(-50));
  };

  const visualizeAudio = () => {
    if (!analyserRef.current || !isRecording) return;
    
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current.getByteTimeDomainData(dataArray);
    
    // Calculate RMS level
    let sumSquares = 0;
    for (let i = 0; i < bufferLength; i++) {
      const normalized = (dataArray[i] - 128) / 128;
      sumSquares += normalized * normalized;
    }
    const rms = Math.sqrt(sumSquares / bufferLength);
    const dbLevel = 20 * Math.log10(rms);
    const normalizedLevel = Math.max(0, Math.min(100, (dbLevel + 60) * 1.66));
    
    setAudioLevel(normalizedLevel);
    animationRef.current = requestAnimationFrame(visualizeAudio);
  };

  const startAudioTest = async () => {
    try {
      addLog('Starting audio test...');
      setError(null);
      
      // Request microphone
      const constraints = {
        audio: {
          deviceId: selectedDevice === 'default' ? undefined : { exact: selectedDevice },
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        }
      };
      
      addLog(`Requesting microphone with constraints: ${JSON.stringify(constraints.audio)}`);
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      const track = stream.getAudioTracks()[0];
      const settings = track.getSettings();
      addLog(`Audio track settings: ${JSON.stringify(settings)}`);
      addLog(`Track enabled: ${track.enabled}, muted: ${track.muted}`);
      
      // Create audio context
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      addLog(`Audio context state: ${audioContextRef.current.state}`);
      
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
        addLog('Audio context resumed');
      }
      
      // Create analyser
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      analyserRef.current.smoothingTimeConstant = 0.8;
      source.connect(analyserRef.current);
      
      // Start visualization
      setIsRecording(true);
      visualizeAudio();
      
      // Create media recorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
        ? 'audio/webm;codecs=opus' 
        : 'audio/webm';
      
      addLog(`Using MIME type: ${mimeType}`);
      
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType });
      
      let chunkCount = 0;
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunkCount++;
          addLog(`Chunk ${chunkCount}: ${event.data.size} bytes`);
        }
      };
      
      mediaRecorderRef.current.start(100);
      addLog('Recording started successfully', 'success');
      
    } catch (err) {
      addLog(`Error: ${err.name} - ${err.message}`, 'error');
      setError(err.message);
    }
  };

  const stopAudioTest = () => {
    addLog('Stopping audio test...');
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
        addLog(`Stopped track: ${track.label}`);
      });
      streamRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    
    setIsRecording(false);
    setAudioLevel(0);
    addLog('Audio test stopped', 'success');
  };

  return (
    <div className="audio-debugger">
      <h2>🎤 Audio Debugger</h2>
      
      <div className="control-panel">
        <div className="device-selector">
          <label>Select Microphone:</label>
          <select 
            value={selectedDevice} 
            onChange={(e) => setSelectedDevice(e.target.value)}
            disabled={isRecording}
          >
            <option value="default">Default Microphone</option>
            {devices.map(device => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || `Device ${device.deviceId.substring(0, 8)}...`}
              </option>
            ))}
          </select>
        </div>
        
        <div className="buttons">
          <button 
            onClick={startAudioTest} 
            disabled={isRecording}
            className="start-button"
          >
            Start Test
          </button>
          <button 
            onClick={stopAudioTest} 
            disabled={!isRecording}
            className="stop-button"
          >
            Stop Test
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="audio-meter">
        <label>Audio Level:</label>
        <div className="meter-container">
          <div 
            className="meter-fill" 
            style={{ width: `${audioLevel}%` }}
          />
          <span className="meter-value">{Math.round(audioLevel)}%</span>
        </div>
      </div>

      <div className="log-container">
        <h3>Debug Log</h3>
        <div className="log-entries">
          {logs.map((log, i) => (
            <div key={i} className={`log-entry log-${log.type}`}>
              <span className="log-time">{log.timestamp}</span>
              <span className="log-message">{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AudioDebugger;