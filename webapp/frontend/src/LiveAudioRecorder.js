import React, { useState, useRef, useEffect } from 'react';
import './AudioRecorder.css';

function LiveAudioRecorder({ onStatusChange, model = 'gemini-flash' }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [micDebug, setMicDebug] = useState({
    supported: false,
    devices: [],
    currentDevice: null,
    selectedDeviceId: 'default',
    audioLevel: 0,
    error: null,
    permissionStatus: null
  });
  
  const mediaRecorderRef = useRef(null);
  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    // Check browser support and enumerate devices
    const checkMicrophoneSupport = async () => {
      try {
        const supported = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
        setMicDebug(prev => ({ ...prev, supported }));

        if (supported) {
          // Check permissions first
          if (navigator.permissions && navigator.permissions.query) {
            try {
              const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
              setMicDebug(prev => ({ 
                ...prev, 
                permissionStatus: permissionStatus.state 
              }));
              
              // Listen for permission changes
              permissionStatus.onchange = () => {
                setMicDebug(prev => ({ 
                  ...prev, 
                  permissionStatus: permissionStatus.state 
                }));
                // Re-enumerate devices when permission changes
                enumerateDevices();
              };
            } catch (e) {
              console.log('Permissions API not supported');
            }
          }

          // Enumerate devices
          const enumerateDevices = async () => {
            try {
              // First try to enumerate without permission
              let devices = await navigator.mediaDevices.enumerateDevices();
              let audioInputs = devices.filter(device => device.kind === 'audioinput');
              
              // If no devices or only default device, try to trigger permission
              if (audioInputs.length === 0 || (audioInputs.length === 1 && !audioInputs[0].label)) {
                console.log('No labeled devices found, attempting to request permission...');
                try {
                  // Request permission by getting user media
                  const tempStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                  // Stop the stream immediately
                  tempStream.getTracks().forEach(track => track.stop());
                  
                  // Re-enumerate after permission
                  devices = await navigator.mediaDevices.enumerateDevices();
                  audioInputs = devices.filter(device => device.kind === 'audioinput');
                } catch (permError) {
                  console.log('Permission request failed:', permError.message);
                }
              }
              
              setMicDebug(prev => ({ 
                ...prev, 
                devices: audioInputs.map(d => ({
                  id: d.deviceId,
                  label: d.label || `Microphone ${d.deviceId.substring(0, 5)}...`
                }))
              }));
            } catch (err) {
              console.error('Error enumerating devices:', err);
              setMicDebug(prev => ({ ...prev, error: err.message }));
            }
          };

          await enumerateDevices();

          // Also listen for device changes
          if (navigator.mediaDevices.ondevicechange !== undefined) {
            navigator.mediaDevices.ondevicechange = enumerateDevices;
          }
        }
      } catch (err) {
        setMicDebug(prev => ({ ...prev, error: err.message }));
      }
    };

    checkMicrophoneSupport();
    
    // Cleanup on unmount
    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  const updateAudioLevel = () => {
    if (analyserRef.current && isRecording) {
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setMicDebug(prev => ({ ...prev, audioLevel: Math.round(average) }));
      animationRef.current = requestAnimationFrame(updateAudioLevel);
    }
  };

  const connectWebSocket = () => {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`ws://localhost:8000/ws/audio-live`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        wsRef.current = ws;
        resolve(ws);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'text') {
            // Append text to transcript
            setTranscript(prev => prev + data.content);
          } else if (data.type === 'turn_complete') {
            // Add newline after complete response
            setTranscript(prev => prev + '\n\n');
          } else if (data.type === 'error') {
            console.error('Server error:', data.message);
            setMicDebug(prev => ({ ...prev, error: data.message }));
          }
        } catch (e) {
          console.error('Error parsing message:', e);
        }
      };
    });
  };

  const startRecording = async () => {
    try {
      // Connect WebSocket first
      await connectWebSocket();
      
      // Use selected device
      const selectedDevice = micDebug.selectedDeviceId;
      
      // Try different constraint combinations with the selected device
      const constraints = [
        { 
          audio: { 
            deviceId: selectedDevice,
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true
          } 
        },
        { audio: { deviceId: selectedDevice } }, // Selected device
        { audio: true }, // Fallback to any device
      ];
      
      let stream = null;
      let lastError = null;
      
      // Try each constraint set
      for (const constraint of constraints) {
        try {
          console.log('Trying constraints:', constraint);
          stream = await navigator.mediaDevices.getUserMedia(constraint);
          console.log('Success with constraints:', constraint);
          break;
        } catch (err) {
          console.log('Failed with constraints:', constraint, err.message);
          lastError = err;
        }
      }
      
      if (!stream) {
        throw lastError || new Error('Could not access microphone with any constraints');
      }
      
      streamRef.current = stream;
      
      // Get active track info
      const audioTrack = stream.getAudioTracks()[0];
      setMicDebug(prev => ({ 
        ...prev, 
        currentDevice: audioTrack.label,
        error: null 
      }));

      // Set up audio analysis
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);
      updateAudioLevel();

      // Create MediaRecorder with smaller time slices for real-time streaming
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 16000
      });
      mediaRecorderRef.current = mediaRecorder;

      // Send audio chunks as they become available
      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0 && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          // Convert blob to base64
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64Audio = reader.result.split(',')[1];
            wsRef.current.send(JSON.stringify({
              type: 'audio_chunk',
              audio: base64Audio
            }));
          };
          reader.readAsDataURL(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        // Send completion message
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'audio_complete'
          }));
        }
        
        // Cancel animation frame
        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current);
        }
        
        // Stop all tracks and clean up
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
        if (audioContextRef.current) {
          audioContextRef.current.close();
          audioContextRef.current = null;
        }
      };

      // Start recording with 100ms time slices for near real-time streaming
      mediaRecorder.start(100);
      setIsRecording(true);
      
      // Clear previous transcript
      setTranscript('');
      
      // Notify parent component
      if (onStatusChange) {
        onStatusChange({ recording: true, connected: true });
      }
    } catch (error) {
      console.error('Error accessing microphone:', error.name, '-', error.message);
      setMicDebug(prev => ({ ...prev, error: error.message }));
      
      // Show more helpful error messages
      let helpMessage = '';
      if (error.name === 'NotFoundError') {
        helpMessage = 'No microphone found. Please connect a microphone and refresh the page.';
      } else if (error.name === 'NotAllowedError') {
        helpMessage = 'Microphone permission denied. Please allow microphone access in your browser settings.';
      } else if (error.name === 'NotReadableError') {
        helpMessage = 'Microphone is in use by another application.';
      }
      
      alert(helpMessage || `Could not access microphone: ${error.message}`);
      
      // Close WebSocket if open
      if (wsRef.current) {
        wsRef.current.close();
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setMicDebug(prev => ({ ...prev, audioLevel: 0 }));
      
      // Close WebSocket
      if (wsRef.current) {
        wsRef.current.close();
      }
      
      // Notify parent component
      if (onStatusChange) {
        onStatusChange({ recording: false, connected: false });
      }
    }
  };

  const requestPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      // Re-check devices
      window.location.reload();
    } catch (err) {
      console.error('Permission request failed:', err);
    }
  };

  return (
    <div className="audio-recorder">
      <h3>🎤 Live Audio Streaming (Gemini Live API)</h3>
      
      <button
        onClick={isRecording ? stopRecording : startRecording}
        className={`record-button ${isRecording ? 'recording' : ''}`}
        data-testid="record-button"
        disabled={!micDebug.supported}
      >
        {isRecording ? '🛑 Stop Live Stream' : '🎤 Start Live Stream'}
      </button>
      
      {/* Connection Status */}
      <div className="connection-status" style={{ margin: '10px 0' }}>
        <p>WebSocket: {isConnected ? '✅ Connected' : '❌ Disconnected'}</p>
      </div>
      
      {/* Audio Device Selector */}
      {micDebug.devices.length > 0 && (
        <div className="device-selector" style={{ margin: '15px 0' }}>
          <label htmlFor="audio-device-select" style={{ marginRight: '10px' }}>
            Select Microphone:
          </label>
          <select
            id="audio-device-select"
            value={micDebug.selectedDeviceId}
            onChange={(e) => setMicDebug(prev => ({ ...prev, selectedDeviceId: e.target.value }))}
            disabled={isRecording}
            style={{
              padding: '5px 10px',
              borderRadius: '4px',
              border: '1px solid #61dafb',
              backgroundColor: '#282c34',
              color: 'white',
              fontSize: '14px'
            }}
          >
            <option value="default">Default Microphone</option>
            {micDebug.devices.map((device) => (
              <option key={device.id} value={device.id}>
                {device.label}
              </option>
            ))}
          </select>
        </div>
      )}
      
      {/* Live Transcript */}
      {transcript && (
        <div className="transcript" style={{
          margin: '20px 0',
          padding: '15px',
          backgroundColor: '#1e1e1e',
          borderRadius: '8px',
          border: '1px solid #61dafb',
          maxHeight: '300px',
          overflowY: 'auto'
        }}>
          <h4>Live Transcript:</h4>
          <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{transcript}</pre>
        </div>
      )}
      
      {/* Microphone Debug Info */}
      <div className="mic-debug" data-testid="mic-debug">
        <h5>Microphone Debug Info</h5>
        <p>Browser Support: {micDebug.supported ? '✅ Yes' : '❌ No'}</p>
        {micDebug.permissionStatus && (
          <p>Permission: {
            micDebug.permissionStatus === 'granted' ? '✅ Granted' :
            micDebug.permissionStatus === 'denied' ? '❌ Denied' :
            '⏳ Not determined'
          }</p>
        )}
        <p>Available Devices: {micDebug.devices.length}</p>
        {micDebug.devices.length === 0 && micDebug.supported && (
          <div className="warning">
            <p>⚠️ No microphone found. Possible issues:</p>
            <ul style={{ fontSize: '10px', textAlign: 'left' }}>
              <li>Browser needs permission (click button below)</li>
              <li>Microphone is disabled in browser settings</li>
              <li>Another app is using the microphone</li>
              <li>Browser security policy blocking access</li>
            </ul>
            <button 
              onClick={requestPermission}
              style={{ fontSize: '12px', padding: '5px 10px', marginTop: '5px' }}
            >
              Request Permission
            </button>
          </div>
        )}
        {isRecording && (
          <>
            <p>Active Device: {micDebug.currentDevice}</p>
            <p>Audio Level: {micDebug.audioLevel}</p>
            <div className="audio-level-bar">
              <div 
                className="audio-level-fill" 
                style={{ width: `${(micDebug.audioLevel / 255) * 100}%` }}
              />
            </div>
          </>
        )}
        {micDebug.error && (
          <p className="error">Error: {micDebug.error}</p>
        )}
      </div>
    </div>
  );
}

export default LiveAudioRecorder;