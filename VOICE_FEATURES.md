# Voice Features Documentation

## 🔊 Text-to-Speech Implementation with Open Source Models

### Overview
The AI Call Center app includes advanced text-to-speech (TTS) functionality using completely open-source and free models, eliminating dependency on paid APIs like Google TTS.

### Voice Models

#### 👤 Customer Voice (US Neural)
- **Primary**: Aria Neural (US Female) - Natural, conversational tone
- **Alternative**: Christopher Neural (US Male) - Friendly, approachable
- **Engine**: Microsoft Edge TTS (free, high-quality)
- **Characteristics**: Slightly faster speech rate, casual tone

#### 👨‍💼 Agent Voice (UK Neural)
- **Primary**: Sonia Neural (UK Female) - Professional, clear
- **Alternative**: Ryan Neural (UK Male) - Authoritative, helpful
- **Engine**: Microsoft Edge TTS (free, high-quality)
- **Characteristics**: Measured pace, professional tone

### TTS Engines

#### Offline Mode (pyttsx3)
- **Advantages**: 
  - Fastest processing (no internet required)
  - Complete privacy (local processing)
  - Customizable speech rate (150-300 WPM)
  - No API limits or costs
- **Features**:
  - Uses system-installed voices
  - Real-time speech synthesis
  - Adjustable parameters

#### Edge TTS Mode (Microsoft Neural Voices)
- **Advantages**:
  - Studio-quality neural voice synthesis
  - Multiple high-quality voice options
  - Natural prosody and intonation
  - Completely free (no API key required)
- **Features**:
  - Neural voice models from Microsoft
  - Different accents and genders
  - Professional-grade audio quality
  - Async processing for responsiveness

### Key Benefits of Open Source Approach

#### 🆓 Cost-Free Operation
- No API keys or usage limits
- No subscription fees
- Unlimited voice synthesis

#### 🔒 Privacy & Security
- Local processing option available
- No data sent to third-party services (offline mode)
- Complete control over voice data

#### 🚀 Performance
- Fast offline processing
- High-quality neural voices
- Reliable operation without internet dependency

### Technical Implementation

#### Dependencies
```python
pyttsx3>=2.90      # Offline TTS engine
edge-tts>=6.1.0    # Microsoft Edge TTS (free)
pygame>=2.1.0      # Audio playback
asyncio            # Async processing
```

#### Key Components
1. **TTSManager Class**: Handles both offline and Edge TTS
2. **Async Voice Generation**: Non-blocking Edge TTS processing
3. **Voice Selection**: Smart voice assignment based on persona
4. **Error Handling**: Graceful fallback between engines

### Voice Options

#### Customer Voices
- **Aria Neural (Default)**: Natural US female voice
- **Christopher Neural (Alt)**: Friendly US male voice

#### Agent Voices  
- **Sonia Neural (Default)**: Professional UK female voice
- **Ryan Neural (Alt)**: Authoritative UK male voice

### Usage Instructions

1. **Choose TTS Mode**: Select between "offline" or "edge-tts"
2. **Voice Options**: Toggle alternative voices for variety
3. **Test Voices**: Use pre-call testing to verify audio
4. **Start Conversation**: Auto-speak or manual playback
5. **Control Audio**: Stop, replay, or switch modes anytime

### Features

#### 🎛️ Voice Controls
- **Auto-speak**: Automatically speak new messages
- **Manual Replay**: Replay any message on demand
- **Stop Audio**: Stop current speech synthesis
- **Voice Testing**: Test both customer and agent voices

#### 📊 Voice Analytics
- **Audio Coverage**: Percentage of messages with audio playback
- **Voice Metrics**: Track speech synthesis success rate
- **Real-time Monitoring**: Live voice quality indicators

#### 🎪 Interactive Elements
- **Voice Mode Toggle**: Switch between offline/online TTS
- **Speech Rate Control**: Adjust speaking speed (offline mode)
- **Voice Testing**: Pre-call voice engine verification

### Technical Implementation

#### Dependencies
```python
pyttsx3>=2.90    # Offline TTS engine
gTTS>=2.3.0      # Google Text-to-Speech
pygame>=2.1.0    # Audio playback
```

#### Key Components
1. **TTSManager Class**: Handles both offline and online TTS
2. **Voice Setup**: Configures different voices for personas
3. **Audio Playback**: Manages audio file creation and playback
4. **Error Handling**: Graceful fallback for TTS failures

### Usage Instructions

1. **Start a Call**: Navigate to "🎯 Live Call Simulator"
2. **Configure Voice**: Choose offline/online mode and settings
3. **Test Voices**: Use voice testing buttons before starting
4. **Simulate Conversation**: Click speaking buttons for realistic audio
5. **Control Playback**: Use stop/replay buttons as needed

### Voice Quality Optimization

#### For Best Results:
- **Offline Mode**: Ensure system has good quality TTS voices installed
- **Online Mode**: Stable internet connection for cloud TTS
- **Audio Setup**: Good speakers or headphones for clear playback
- **Environment**: Quiet environment for better audio experience

### Troubleshooting

#### Common Issues:
- **No Audio**: Check system audio settings and volume
- **TTS Errors**: Try switching between offline/online modes
- **Voice Quality**: Install additional system voices for offline mode
- **Network Issues**: Use offline mode if internet is unstable

### Future Enhancements

#### Planned Features:
- **Real-time Speech Recognition**: Actual voice input processing
- **Voice Cloning**: Custom voice models for specific personas
- **Emotion Synthesis**: Emotional tone in voice synthesis
- **Multi-language Support**: Support for multiple languages
- **Voice Interruption**: Realistic conversation interruptions
