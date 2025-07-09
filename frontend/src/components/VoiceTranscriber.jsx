import React, { useState, useRef, useEffect } from 'react';
import { getWsBaseUrl } from '@/lib/api';

const VoiceTranscriber = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcriptions, setTranscriptions] = useState([]);
  const [error, setError] = useState(null);
  const websocketRef = useRef(null);
  const audioContextRef = useRef(null);
  const streamRef = useRef(null);
  const processorRef = useRef(null);
  const inputStreamRef = useRef(null);

  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, []);

  const startRecording = async () => {
    try {
      // Reset state
      setError(null);
      setTranscriptions([]);

      // Get microphone stream
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          channelCount: 1,
          sampleRate: 44100,
          sampleSize: 16
        } 
      });
      streamRef.current = stream;

      // Initialize WebSocket
      const wsBaseUrl = getWsBaseUrl();
      websocketRef.current = new WebSocket(`${wsBaseUrl}/ws/transcribe`);
      
      websocketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'transcription') {
          setTranscriptions(prev => [...prev, {
            speaker: data.speaker,
            text: data.text,
            timestamp: new Date().toLocaleTimeString()
          }]);
        } else if (data.type === 'error') {
          setError(data.message);
          stopRecording();
        }
      };

      websocketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Connection error. Please try again.');
        stopRecording();
      };

      websocketRef.current.onopen = () => {
        // Initialize audio processing once WebSocket is connected
        audioContextRef.current = new AudioContext({
          sampleRate: 44100,
        });

        // Create audio source from microphone stream
        inputStreamRef.current = audioContextRef.current.createMediaStreamSource(stream);

        // Create script processor for raw PCM data
        processorRef.current = audioContextRef.current.createScriptProcessor(4096, 1, 1);
        
        processorRef.current.onaudioprocess = (e) => {
          if (websocketRef.current?.readyState === WebSocket.OPEN) {
            // Get raw audio data
            const inputData = e.inputBuffer.getChannelData(0);
            
            // Convert to 16-bit PCM
            const pcmData = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
              pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
            }
            
            // Send the PCM data to the server
            websocketRef.current.send(pcmData.buffer);
          }
        };

        // Connect the audio nodes
        inputStreamRef.current.connect(processorRef.current);
        processorRef.current.connect(audioContextRef.current.destination);
        
        setIsRecording(true);
      };

    } catch (err) {
      setError('Failed to access microphone. Please check your permissions.');
      console.error('Setup error:', err);
      stopRecording();
    }
  };

  const stopRecording = () => {
    // Stop recording
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Cleanup audio context
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (inputStreamRef.current) {
      inputStreamRef.current.disconnect();
      inputStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Close WebSocket
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }

    setIsRecording(false);
  };

  return (
    <div className="container mx-auto p-4">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">Voice Transcription</h2>
        
        <div className="mb-6">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`px-6 py-3 rounded-lg font-semibold ${
              isRecording
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            } flex items-center gap-2`}
          >
            {isRecording ? (
              <>
                <span className="w-3 h-3 bg-white rounded-full animate-pulse"></span>
                Stop Listening
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
                Start Listening
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <div className="bg-gray-50 p-4 rounded-lg min-h-[200px] space-y-4">
          <h3 className="text-lg font-semibold mb-2">Live Transcription:</h3>
          {transcriptions.length > 0 ? (
            <div className="space-y-4">
              {transcriptions.map((item, index) => (
                <div 
                  key={index} 
                  className={`p-3 rounded-lg ${
                    item.speaker === 'Person 1' 
                      ? 'bg-blue-50 border border-blue-100' 
                      : 'bg-green-50 border border-green-100'
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-sm">
                      {item.speaker}
                    </span>
                    <span className="text-xs text-gray-500">
                      {item.timestamp}
                    </span>
                  </div>
                  <p className="text-gray-700">{item.text}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic">
              {isRecording ? 'Listening... Start speaking.' : 'Click "Start Listening" to begin transcription.'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceTranscriber; 