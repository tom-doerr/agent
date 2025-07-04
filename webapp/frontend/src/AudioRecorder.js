import React, { useState, useRef, useEffect } from 'react';
import './AudioRecorder.css';

function AudioRecorder({ onAudioData, model = 'gemini-flash' }) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
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
  const chunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);

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

  const startRecording = async () => {
    try {
      // Use selected device
      const selectedDevice = micDebug.selectedDeviceId;
      
      // Try different constraint combinations with the selected device
      const constraints = [
        { audio: { deviceId: selectedDevice } }, // Selected device
        { audio: { deviceId: { exact: selectedDevice } } }, // Exact device
        { audio: { 
          deviceId: selectedDevice,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }},
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

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        
        // Cancel animation frame
        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current);
        }
        
        // Convert blob to base64 for direct model input
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64Audio = reader.result.split(',')[1]; // Remove data URL prefix
          // Send raw audio data to parent component
          onAudioData({
            blob: audioBlob,
            base64: base64Audio,
            mimeType: 'audio/webm',
            deviceLabel: micDebug.currentDevice
          });
        };
        reader.readAsDataURL(audioBlob);
        
        // Stop all tracks and clean up
        stream.getTracks().forEach(track => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
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
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setMicDebug(prev => ({ ...prev, audioLevel: 0 }));
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
      <button
        onClick={isRecording ? stopRecording : startRecording}
        className={`record-button ${isRecording ? 'recording' : ''}`}
        data-testid="record-button"
      >
        {isRecording ? '🛑 Stop Recording' : '🎤 Start Recording'}
      </button>
      
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
        {micDebug.devices.length > 0 && (
          <ul>
            {micDebug.devices.map((device, i) => (
              <li key={i}>{device.label}</li>
            ))}
          </ul>
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
      
      {audioBlob && !isRecording && (
        <div className="audio-preview">
          <audio controls src={URL.createObjectURL(audioBlob)} />
        </div>
      )}
    </div>
  );
}

export default AudioRecorder;