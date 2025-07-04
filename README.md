# AI-Driven Call Center with Live Insights

A comprehensive AI-powered Streamlit application that simulates real-time call center operations with live suggestions and training data management.

## 🚀 Key Features

### 🎯 Live Call Simulator
- **Real-time Voice Call Simulation**: WebRTC-based call interface
- **Speech-to-Text Processing**: Live transcript generation (simulated)
- **AI-Powered Suggestions**: Context-aware agent assistance
- **Sentiment Analysis**: Real-time customer emotion detection
- **Low Latency Processing**: Optimized for real-time interactions

### 📚 Training Data Manager
- **Multi-format File Ingestion**: PDF, DOC, TXT, CSV support
- **Web Crawling**: Automated website content extraction
- **Data Preprocessing**: Advanced text cleaning and chunking
- **CRUD Operations**: Complete data management interface
- **Quality Metrics**: Data completeness and accuracy tracking

### 📊 Additional Features
- **Interactive Visualizations**: Plotly-powered charts
- **Dynamic Widgets**: Comprehensive UI components
- **File Processing**: CSV analysis and upload
- **Modern UI**: Responsive design with custom styling

## 🏗️ Architecture

```
AI Call Center App
├── Live Call Simulator
│   ├── WebRTC Simulation
│   ├── Real-time Transcription
│   ├── AI Suggestion Engine
│   └── Sentiment Analysis
├── Training Data Pipeline
│   ├── File Upload & Processing
│   ├── Web Source Management
│   ├── Text Input Interface
│   └── Data Quality Analytics
└── Core Features
    ├── Data Visualization
    ├── Interactive Widgets
    └── File Management
```

## Setup and Installation

1. **Clone or download this project**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## Project Structure

```
v2/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Usage

- Use the sidebar to navigate between different pages
- Explore data visualizations with different chart types
- Interact with various widgets on the widgets page
- Upload CSV files to analyze your own data

## Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly**: Interactive visualizations
- **pyttsx3**: Offline text-to-speech engine
- **Edge TTS**: Microsoft's free neural voice synthesis
- **Pygame**: Audio playback management
- **WebRTC**: Real-time communication (simulated)

## Project Objectives

This application demonstrates:

### ✅ Proper Data Ingestion & Preprocessing
- Multi-format file upload and processing
- Web crawling for content extraction
- Text preprocessing and chunking
- Data quality validation

### ✅ Real-Time Processing and Low Latency
- Simulated WebRTC connections
- Live transcript generation
- Real-time AI suggestions
- Instant sentiment analysis

### ✅ Contextual Understanding
- Context-aware suggestion engine
- Historical conversation analysis
- Intelligent response recommendations
- Sentiment-based interactions

### ✅ Interactive UI Chatbot Interface
- Modern chat interface design
- Real-time message updates
- Visual sentiment indicators
- Agent assistance panels

## Demo Features

> **Note**: This is a demonstration application with simulated functionality. No actual speech processing or AI models are running - all interactions use dummy data and randomized responses to showcase the interface and user experience.

## Future Enhancements

- Integration with actual speech-to-text APIs
- Real AI model integration for suggestions
- Live WebRTC implementation
- Database backend for persistent storage
- Advanced analytics and reporting
