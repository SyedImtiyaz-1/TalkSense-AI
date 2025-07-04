import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import time
import random
import pyttsx3
import pygame
import edge_tts
import asyncio
import io
import threading
import tempfile
import os
import concurrent.futures

# Set page configuration
st.set_page_config(
    page_title="AI Call Center - Live Insights",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    try:
        css_file_path = os.path.join(os.path.dirname(__file__), "style.css")
        with open(css_file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ CSS file not found. Using default styling.")
        pass  # CSS file not found, continue without styling

load_css()

# Text-to-Speech Helper Functions with Open Source Models
class TTSManager:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Initialize pyttsx3 engine for offline TTS
        try:
            self.engine = pyttsx3.init()
            self.setup_voices()
        except:
            self.engine = None
            st.warning("⚠️ Offline TTS engine not available. Using Edge TTS only.")
        
        # Edge TTS voices (high quality, free)
        self.customer_voice_edge = "en-US-AriaNeural"  # US female voice
        self.agent_voice_edge = "en-GB-SoniaNeural"    # UK female voice
        
        # Alternative voices
        self.customer_voice_alt = "en-US-ChristopherNeural"  # US male voice
        self.agent_voice_alt = "en-GB-RyanNeural"           # UK male voice
    
    def setup_voices(self):
        """Setup different voices for customer and agent using pyttsx3"""
        if self.engine:
            voices = self.engine.getProperty('voices')
            if len(voices) >= 2:
                # Use different voices for customer and agent
                self.customer_voice = voices[0].id
                self.agent_voice = voices[1].id if len(voices) > 1 else voices[0].id
            else:
                self.customer_voice = voices[0].id if voices else None
                self.agent_voice = voices[0].id if voices else None
    
    def speak_offline(self, text, speaker_type="customer", rate=200):
        """Use pyttsx3 for offline TTS"""
        if not self.engine:
            return False
        
        try:
            # Set voice based on speaker type
            if speaker_type == "customer":
                self.engine.setProperty('voice', self.customer_voice)
                self.engine.setProperty('rate', rate)  # Slightly faster for customer
            else:
                self.engine.setProperty('voice', self.agent_voice)
                self.engine.setProperty('rate', rate - 20)  # Slower, more professional for agent
            
            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            st.error(f"Offline TTS Error: {str(e)}")
            return False
    
    async def _generate_edge_tts_async(self, text, voice):
        """Async function to generate speech using Edge TTS"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_filename = tmp_file.name
            
            # Generate speech
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_filename)
            
            return tmp_filename
        except Exception as e:
            st.error(f"Edge TTS Generation Error: {str(e)}")
            return None
    
    def speak_edge_tts(self, text, speaker_type="customer", use_alt_voice=False):
        """Use Edge TTS for high-quality speech synthesis"""
        try:
            # Select voice based on speaker type
            if speaker_type == "customer":
                voice = self.customer_voice_alt if use_alt_voice else self.customer_voice_edge
            else:
                voice = self.agent_voice_alt if use_alt_voice else self.agent_voice_edge
            
            # Run async function in a new event loop
            try:
                # Try to get existing event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a new thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._generate_edge_tts_async(text, voice))
                        tmp_filename = future.result(timeout=30)
                else:
                    tmp_filename = loop.run_until_complete(self._generate_edge_tts_async(text, voice))
            except RuntimeError:
                # No event loop, create new one
                tmp_filename = asyncio.run(self._generate_edge_tts_async(text, voice))
            
            if tmp_filename and os.path.exists(tmp_filename):
                # Play the audio
                pygame.mixer.music.load(tmp_filename)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Clean up temporary file with retry
                def cleanup_file(filename, max_retries=3):
                    for i in range(max_retries):
                        try:
                            if os.path.exists(filename):
                                os.unlink(filename)
                            break
                        except OSError:
                            if i < max_retries - 1:
                                time.sleep(0.5)  # Wait and retry
                            # If final retry fails, ignore (file will be cleaned up by system)
                
                cleanup_file(tmp_filename)
                
                return True
            else:
                return False
                
        except Exception as e:
            st.error(f"Edge TTS Error: {str(e)}")
            return False
    
    def speak_online(self, text, speaker_type="customer", use_alt_voice=False):
        """Use Edge TTS as the online option (replaces Google TTS)"""
        return self.speak_edge_tts(text, speaker_type, use_alt_voice)
    
    def stop_audio(self):
        """Stop any currently playing audio"""
        try:
            if self.engine:
                self.engine.stop()
            pygame.mixer.music.stop()
        except:
            pass
    
    def get_available_voices(self):
        """Get list of available voices for each mode"""
        voices_info = {
            "offline": [],
            "edge_tts": {
                "customer": {
                    "primary": "en-US-AriaNeural (US Female)",
                    "alternative": "en-US-ChristopherNeural (US Male)"
                },
                "agent": {
                    "primary": "en-GB-SoniaNeural (UK Female)", 
                    "alternative": "en-GB-RyanNeural (UK Male)"
                }
            }
        }
        
        # Get offline voices
        if self.engine:
            try:
                system_voices = self.engine.getProperty('voices')
                for voice in system_voices:
                    voices_info["offline"].append(voice.name)
            except:
                voices_info["offline"] = ["System Default"]
        
        return voices_info

# Initialize TTS Manager
@st.cache_resource
def get_tts_manager():
    return TTSManager()

tts_manager = get_tts_manager()

# Main app
def main():
    # Title and description
    st.title("🚀 Simple Streamlit App")
    st.markdown("---")
    st.markdown("Welcome to this simple Streamlit application! This app demonstrates various Streamlit features.")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Home", "Data Visualization", "Interactive Widgets", "File Upload", "🎯 Live Call Simulator", "📚 Training Data Manager"]
    )
    
    if page == "Home":
        home_page()
    elif page == "Data Visualization":
        data_viz_page()
    elif page == "Interactive Widgets":
        widgets_page()
    elif page == "File Upload":
        file_upload_page()
    elif page == "🎯 Live Call Simulator":
        live_call_simulator_page()
    elif page == "📚 Training Data Manager":
        training_data_manager_page()

def home_page():
    st.header("🏠 Home Page")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("About This App")
        st.write("""
        This is a comprehensive AI-driven application that showcases:
        - **🎯 Live Call Simulator**: Real-time voice call simulation with TTS
        - **🔊 Dual Voice Models**: Different voices for customer and agent
        - **📚 Training Data Manager**: Complete data ingestion and preprocessing pipeline
        - **📊 Data Visualization**: Interactive charts and graphs
        - **🎛️ Widgets**: Various input components
        - **📁 File Upload**: CSV file processing
        - **🔄 Layout**: Multi-column layouts and sidebars
        """)
        
        st.info("� Navigate through different pages using the sidebar to explore AI-powered features!")
    
    with col2:
        st.subheader("🔊 Voice AI Features")
        
        st.markdown("**🎯 Live Call with Voice:**")
        st.markdown("- Real-time speech synthesis (TTS)")
        st.markdown("- Dual voice models (US/UK accents)")
        st.markdown("- Offline & Online TTS engines")
        st.markdown("- Voice analytics & controls")
        
        st.markdown("**🤖 AI Capabilities:**")
        st.markdown("- Context-aware suggestions")
        st.markdown("- Sentiment analysis")
        st.markdown("- Real-time processing")
        st.markdown("- Voice-enabled interactions")
    
    # AI Metrics
    st.subheader("🤖 AI System Metrics")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Active Calls", random.randint(15, 45), "↗️ 5")
    with col_b:
        st.metric("Training Data", f"{random.randint(500, 999)} MB", "↗️ 23 MB")
    with col_c:
        st.metric("Model Accuracy", f"{random.randint(92, 99)}.{random.randint(1, 9)}%", "↗️ 0.3%")
    with col_d:
        st.metric("Voice Quality", f"{random.randint(95, 99)}.{random.randint(1, 9)}%", "↗️ 0.1%")

def data_viz_page():
    st.header("📊 Data Visualization")
    
    # Generate sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'Sales': np.random.normal(1000, 200, 100).cumsum(),
        'Category': np.random.choice(['A', 'B', 'C'], 100),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 100)
    })
    
    st.subheader("Sample Sales Data")
    
    # Chart type selection
    chart_type = st.selectbox("Select Chart Type:", ["Line Chart", "Bar Chart", "Scatter Plot"])
    
    if chart_type == "Line Chart":
        fig = px.line(data, x='Date', y='Sales', title='Sales Over Time')
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Bar Chart":
        category_sales = data.groupby('Category')['Sales'].sum().reset_index()
        fig = px.bar(category_sales, x='Category', y='Sales', title='Sales by Category')
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Scatter Plot":
        fig = px.scatter(data, x='Date', y='Sales', color='Category', title='Sales Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Display raw data
    if st.checkbox("Show Raw Data"):
        st.dataframe(data.head(20))

def widgets_page():
    st.header("🎛️ Interactive Widgets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Widgets")
        
        # Text input
        name = st.text_input("Enter your name:", "John Doe")
        
        # Number input
        age = st.number_input("Enter your age:", min_value=0, max_value=120, value=25)
        
        # Slider
        rating = st.slider("Rate this app:", 1, 10, 5)
        
        # Select box
        favorite_color = st.selectbox("Favorite color:", ["Red", "Blue", "Green", "Yellow"])
        
        # Checkbox
        subscribe = st.checkbox("Subscribe to newsletter")
        
        # Date input
        birth_date = st.date_input("Birth date:", datetime(1990, 1, 1))
    
    with col2:
        st.subheader("Your Inputs")
        st.write(f"**Name:** {name}")
        st.write(f"**Age:** {age}")
        st.write(f"**Rating:** {rating}/10")
        st.write(f"**Favorite Color:** {favorite_color}")
        st.write(f"**Newsletter:** {'Yes' if subscribe else 'No'}")
        st.write(f"**Birth Date:** {birth_date}")
        
        if st.button("Submit Form"):
            st.success("Form submitted successfully! 🎉")
            st.balloons()

def file_upload_page():
    st.header("📁 File Upload")
    
    st.write("Upload a CSV file to analyze your data:")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            st.success(f"File uploaded successfully! Shape: {df.shape}")
            
            # Display basic info
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Data Preview")
                st.dataframe(df.head())
            
            with col2:
                st.subheader("Data Info")
                st.write(f"**Rows:** {df.shape[0]}")
                st.write(f"**Columns:** {df.shape[1]}")
                st.write("**Column Names:**")
                for col in df.columns:
                    st.write(f"- {col}")
            
            # Basic statistics for numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                st.subheader("Numeric Columns Statistics")
                st.dataframe(df[numeric_columns].describe())
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    else:
        st.info("Please upload a CSV file to get started.")

def live_call_simulator_page():
    st.header("🎯 Live Call Simulator with Voice Synthesis")
    st.markdown("---")
    st.markdown("**AI-Driven Live Call Insights with Real-time Voice Synthesis**")
    
    # Initialize session state for chat history and call status
    if 'call_active' not in st.session_state:
        st.session_state.call_active = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'suggestions_history' not in st.session_state:
        st.session_state.suggestions_history = []
    if 'call_duration' not in st.session_state:
        st.session_state.call_duration = 0
    if 'auto_speak' not in st.session_state:
        st.session_state.auto_speak = True
    if 'tts_mode' not in st.session_state:
        st.session_state.tts_mode = "offline"
    
    # Call Control Panel
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        st.subheader("📞 Call Control")
        if not st.session_state.call_active:
            if st.button("🟢 Start Call", type="primary"):
                st.session_state.call_active = True
                st.session_state.chat_history = []
                st.session_state.suggestions_history = []
                st.session_state.call_duration = 0
                st.rerun()
        else:
            col_end, col_stop = st.columns(2)
            with col_end:
                if st.button("🔴 End Call", type="secondary"):
                    st.session_state.call_active = False
                    tts_manager.stop_audio()
                    st.rerun()
            with col_stop:
                if st.button("⏹️ Stop Audio"):
                    tts_manager.stop_audio()
    
    with col2:
        st.subheader("📊 Call Status")
        if st.session_state.call_active:
            st.success("🟢 Call Active")
            st.metric("Duration", f"{st.session_state.call_duration}s")
        else:
            st.info("⚪ Call Inactive")
    
    with col3:
        st.subheader("🎛️ Settings")
        auto_suggestions = st.checkbox("Auto-suggestions", value=True)
        sentiment_analysis = st.checkbox("Sentiment Analysis", value=True)
        
        # TTS Settings
        st.markdown("**🔊 Voice Settings:**")
        st.session_state.auto_speak = st.checkbox("Auto-speak messages", value=st.session_state.auto_speak)
        st.session_state.tts_mode = st.selectbox(
            "TTS Mode", 
            ["offline", "edge-tts"],
            index=0 if st.session_state.tts_mode == "offline" else 1,
            help="Offline: pyttsx3 (faster), Edge-TTS: Microsoft voices (better quality)"
        )
        
        if st.session_state.tts_mode == "offline":
            tts_rate = st.slider("Speech Rate", 150, 300, 200, help="Words per minute")
        else:
            st.info("Using Microsoft Edge TTS with neural voices")
            use_alt_voice = st.checkbox("Use alternative voices", help="Male voices instead of female")
    
    if st.session_state.call_active:
        st.markdown("---")
        
        # Connection Status
        connection_status = st.container()
        with connection_status:
            st.markdown("""
            <div class="connection-status status-connected">
                <span class="status-dot"></span>
                <strong>🟢 Call Active</strong> - WebRTC Connected | Audio Quality: HD Voice | Latency: {}ms
            </div>
            """.format(random.randint(20, 50)), unsafe_allow_html=True)
        
        # Main Chat Interface
        main_col, sidebar_col = st.columns([2, 1])
        
        with main_col:
            st.subheader("💬 Live Conversation")
            
            # Initialize typing indicator state
            if 'typing_customer' not in st.session_state:
                st.session_state.typing_customer = False
            if 'typing_agent' not in st.session_state:
                st.session_state.typing_agent = False
            
            # Display messages using Streamlit components instead of raw HTML
            for msg in st.session_state.chat_history:
                # Create a container for each message
                with st.container():
                    if msg['speaker'] == 'Customer':
                        # Customer message styling
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #007bff, #0056b3);
                            color: white;
                            padding: 10px 15px;
                            margin: 8px 0;
                            border-radius: 18px;
                            max-width: 80%;
                            margin-left: auto;
                            margin-right: 0;
                            border-bottom-right-radius: 5px;
                            box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
                        ">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                                👤 <strong>{msg['speaker']}</strong>
                                <span style="
                                    display: inline-block;
                                    width: 8px;
                                    height: 8px;
                                    border-radius: 50%;
                                    background-color: {'#28a745' if msg.get('sentiment') == 'Positive' else '#ffc107' if msg.get('sentiment') == 'Neutral' else '#dc3545'};
                                "></span>
                            </div>
                            <div style="margin-bottom: 5px; line-height: 1.4;">{msg['text']}</div>
                            <div style="font-size: 0.75em; opacity: 0.8; margin-top: 5px;">{msg['time']}</div>
                            <div style="font-size: 0.7em; opacity: 0.7; margin-top: 3px;">
                                {'🔊 Audio played' if msg.get('audio_played', False) else '🔇 Audio pending' if st.session_state.auto_speak else '🔇 Audio disabled'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Agent message styling
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #28a745, #1e7e34);
                            color: white;
                            padding: 10px 15px;
                            margin: 8px 0;
                            border-radius: 18px;
                            max-width: 80%;
                            margin-left: 0;
                            margin-right: auto;
                            border-bottom-left-radius: 5px;
                            box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
                        ">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                                👨‍💼 <strong>{msg['speaker']}</strong>
                                <span style="
                                    display: inline-block;
                                    width: 8px;
                                    height: 8px;
                                    border-radius: 50%;
                                    background-color: #007bff;
                                "></span>
                            </div>
                            <div style="margin-bottom: 5px; line-height: 1.4;">{msg['text']}</div>
                            <div style="font-size: 0.75em; opacity: 0.8; margin-top: 5px;">{msg['time']}</div>
                            <div style="font-size: 0.7em; opacity: 0.7; margin-top: 3px;">
                                {'🔊 Audio played' if msg.get('audio_played', False) else '🔇 Audio pending' if st.session_state.auto_speak else '🔇 Audio disabled'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Add typing indicators using Streamlit
            if st.session_state.typing_customer:
                st.markdown("""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 10px 15px;
                    margin: 8px 0;
                    margin-right: auto;
                    background: #f1f3f4;
                    border-radius: 18px;
                    max-width: 80px;
                ">
                    <div style="display: flex; gap: 3px;">
                        <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #9e9e9e;"></div>
                        <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #9e9e9e;"></div>
                        <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #9e9e9e;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.session_state.typing_agent:
                st.markdown("""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 10px 15px;
                    margin: 8px 0;
                    margin-left: auto;
                    margin-right: 0;
                    background: #f1f3f4;
                    border-radius: 18px;
                    max-width: 80px;
                ">
                    <div style="display: flex; gap: 3px;">
                        <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #9e9e9e;"></div>
                        <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #9e9e9e;"></div>
                        <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #9e9e9e;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Control buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Customer messages
            customer_messages = [
                "Hi, I'm having trouble with my internet connection.",
                "It's been slow for the past three days.",
                "I've already tried restarting the router.",
                "The speed test shows only 10 Mbps instead of 100.",
                "This is really frustrating. I work from home.",
                "Can you help me fix this issue?",
                "I'm willing to try any troubleshooting steps.",
                "How long will this take to resolve?",
                "I need this fixed as soon as possible.",
                "Thank you for your help with this."
            ]
            
            # Agent responses
            agent_responses = [
                "Thank you for contacting us. I'll help you with your internet issue.",
                "I understand how frustrating slow internet can be.",
                "Let me check your account and connection status.",
                "I can see there might be a signal issue in your area.",
                "Let's try some troubleshooting steps together.",
                "Can you please check if all cables are securely connected?",
                "I'm scheduling a priority technician visit for you.",
                "Is there anything else I can help you with today?",
                "I'll send you a follow-up email with the details.",
                "Thank you for your patience while we resolve this."
            ]
            
            with col1:
                if st.button("👤 Customer Speaks", type="primary"):
                    if customer_messages:
                        msg = random.choice(customer_messages)
                        sentiment = random.choice(["Positive", "Neutral", "Negative"])
                        current_time = datetime.now().strftime("%H:%M:%S")
                        
                        # Add message to chat history
                        new_message = {
                            'speaker': 'Customer',
                            'text': msg,
                            'time': current_time,
                            'sentiment': sentiment,
                            'audio_played': False
                        }
                        st.session_state.chat_history.append(new_message)
                        
                        # Generate AI suggestion for agent
                        if auto_suggestions:
                            suggestions = [
                                "Acknowledge the customer's frustration and apologize for the inconvenience.",
                                "Ask about the specific devices experiencing slow speeds.",
                                "Suggest checking cable connections and running a speed test.",
                                "Offer to schedule a technician visit if needed.",
                                "Provide the customer with a reference number for follow-up.",
                                "Explain the troubleshooting process step by step.",
                                "Ask about recent changes to their network setup.",
                                "Suggest checking for interference from other devices."
                            ]
                            
                            suggestion = random.choice(suggestions)
                            st.session_state.suggestions_history.append({
                                'time': current_time,
                                'suggestion': suggestion,
                                'confidence': random.randint(85, 99)
                            })
                        
                        # Play TTS if enabled
                        if st.session_state.auto_speak:
                            with st.spinner("🔊 Speaking..."):
                                if st.session_state.tts_mode == "offline":
                                    success = tts_manager.speak_offline(msg, "customer", tts_rate if 'tts_rate' in locals() else 200)
                                else:
                                    success = tts_manager.speak_edge_tts(msg, "customer", use_alt_voice if 'use_alt_voice' in locals() else False)
                                
                                if success:
                                    new_message['audio_played'] = True
                                    # Update the message in chat history
                                    st.session_state.chat_history[-1]['audio_played'] = True
                        
                        st.session_state.call_duration += random.randint(5, 15)
                        st.rerun()
            
            with col2:
                if st.button("👨‍💼 Agent Responds", type="primary"):
                    if agent_responses:
                        response = random.choice(agent_responses)
                        current_time = datetime.now().strftime("%H:%M:%S")
                        
                        # Add message to chat history
                        new_message = {
                            'speaker': 'Agent',
                            'text': response,
                            'time': current_time,
                            'sentiment': 'Professional',
                            'audio_played': False
                        }
                        st.session_state.chat_history.append(new_message)
                        
                        # Play TTS if enabled
                        if st.session_state.auto_speak:
                            with st.spinner("🔊 Speaking..."):
                                if st.session_state.tts_mode == "offline":
                                    success = tts_manager.speak_offline(response, "agent", tts_rate - 20 if 'tts_rate' in locals() else 180)
                                else:
                                    success = tts_manager.speak_edge_tts(response, "agent", use_alt_voice if 'use_alt_voice' in locals() else False)
                                
                                if success:
                                    new_message['audio_played'] = True
                                    # Update the message in chat history
                                    st.session_state.chat_history[-1]['audio_played'] = True
                        
                        st.session_state.call_duration += random.randint(3, 10)
                        st.rerun()
            
            with col3:
                if st.button("🔊 Replay Last Customer"):
                    # Replay last customer message
                    customer_msgs = [msg for msg in st.session_state.chat_history if msg['speaker'] == 'Customer']
                    if customer_msgs:
                        last_msg = customer_msgs[-1]['text']
                        with st.spinner("🔊 Replaying..."):
                            if st.session_state.tts_mode == "offline":
                                tts_manager.speak_offline(last_msg, "customer", tts_rate if 'tts_rate' in locals() else 200)
                            else:
                                tts_manager.speak_edge_tts(last_msg, "customer", use_alt_voice if 'use_alt_voice' in locals() else False)
        
            with col4:
                if st.button("🔊 Replay Last Agent"):
                    # Replay last agent message
                    agent_msgs = [msg for msg in st.session_state.chat_history if msg['speaker'] == 'Agent']
                    if agent_msgs:
                        last_msg = agent_msgs[-1]['text']
                        with st.spinner("🔊 Replaying..."):
                            if st.session_state.tts_mode == "offline":
                                tts_manager.speak_offline(last_msg, "agent", tts_rate - 20 if 'tts_rate' in locals() else 180)
                            else:
                                tts_manager.speak_edge_tts(last_msg, "agent", use_alt_voice if 'use_alt_voice' in locals() else False)
            
            with col5:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.chat_history = []
                    st.session_state.suggestions_history = []
                    st.session_state.typing_customer = False
                    st.session_state.typing_agent = False
                    st.success("Chat cleared!")
                    st.rerun()
        
        # Sidebar with Controls and Analytics
        with sidebar_col:
            # WebRTC Status
            st.markdown("### 🌐 Connection Status")
            st.success("🟢 WebRTC Connected")
            st.info(f"🔊 HD Voice Quality")
            st.info(f"⚡ Latency: {random.randint(20, 50)}ms")
            
            # Voice Settings
            st.markdown("### 🎛️ Voice Settings")
            st.info("👤 Customer: US Neural Voice")
            st.info("👨‍💼 Agent: UK Neural Voice")
            if st.session_state.get('tts_mode', 'offline') == 'offline':
                st.info("🖥️ Local TTS Engine")
            else:
                st.info("🌟 Microsoft Edge TTS")
            
            # Quick Actions
            st.markdown("### 📋 Quick Actions")
            if st.button("📋 Generate Summary", use_container_width=True):
                st.success("Call summary generated!")
            if st.button("📧 Send Follow-up", use_container_width=True):
                st.success("Follow-up email queued!")
            if st.button("🎫 Create Ticket", use_container_width=True):
                st.success("Support ticket created!")
            
            # Call Analytics
            st.markdown("### 📊 Call Analytics")
            sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
            for msg in st.session_state.chat_history:
                if msg['speaker'] == 'Customer' and 'sentiment' in msg:
                    sentiment_counts[msg['sentiment']] += 1
            
            for sentiment, count in sentiment_counts.items():
                st.metric(sentiment, count)
            
            # Voice Analytics
            total_messages = len(st.session_state.chat_history)
            audio_played = len([msg for msg in st.session_state.chat_history if msg.get('audio_played', False)])
            
            st.markdown("### 🔊 Voice Metrics")
            st.metric("Total Messages", total_messages)
            st.metric("Audio Played", audio_played)
            if total_messages > 0:
                st.metric("Audio Coverage", f"{(audio_played/total_messages)*100:.1f}%")
            
            # Auto-refresh toggle
            st.markdown("### 🔄 Real-time Updates")
            auto_refresh = st.checkbox("Enable Auto-Refresh", value=False, help="Automatically refresh chat every 3 seconds")
            
            # Simulation mode
            simulate_conversation = st.checkbox("Auto-Simulate Conversation", value=False, help="Automatically generate messages for demo")
            
            if auto_refresh or simulate_conversation:
                # Show real-time status
                st.markdown("🔄 **Real-time mode active**")
                
                                 # Auto-simulation logic
                if simulate_conversation and len(st.session_state.chat_history) < 20:
                    # Randomly add messages from customer or agent
                    if random.random() < 0.3:  # 30% chance to add message each refresh
                        speaker = random.choice(['Customer', 'Agent'])
                        
                        if speaker == 'Customer':
                            customer_messages = [
                                "Hi, I'm having trouble with my internet connection.",
                                "It's been slow for the past three days.",
                                "I've already tried restarting the router.",
                                "The speed test shows only 10 Mbps instead of 100.",
                                "This is really frustrating. I work from home.",
                                "Can you help me fix this issue?",
                                "I'm willing to try any troubleshooting steps.",
                                "How long will this take to resolve?",
                                "I need this fixed as soon as possible.",
                                "Thank you for your help with this."
                            ]
                            
                            # Avoid duplicate messages by checking recent history
                            recent_messages = [msg['text'] for msg in st.session_state.chat_history[-3:] if msg['speaker'] == 'Customer']
                            available_messages = [msg for msg in customer_messages if msg not in recent_messages]
                            
                            if available_messages:
                                msg = random.choice(available_messages)
                                sentiment = random.choice(["Positive", "Neutral", "Negative"])
                                
                                new_message = {
                                    'speaker': 'Customer',
                                    'text': msg,
                                    'time': datetime.now().strftime("%H:%M:%S"),
                                    'sentiment': sentiment,
                                    'audio_played': st.session_state.auto_speak  # Set to True if auto-speak is enabled
                                }
                                
                                # Generate AI suggestion
                                suggestions = [
                                    "Acknowledge the customer's frustration and apologize for the inconvenience.",
                                    "Ask about the specific devices experiencing slow speeds.",
                                    "Suggest checking cable connections and running a speed test.",
                                    "Offer to schedule a technician visit if needed.",
                                    "Provide the customer with a reference number for follow-up.",
                                    "Explain the troubleshooting process step by step.",
                                    "Ask about recent changes to their network setup.",
                                    "Suggest checking for interference from other devices."
                                ]
                                
                                suggestion = random.choice(suggestions)
                                st.session_state.suggestions_history.append({
                                    'time': new_message['time'],
                                    'suggestion': suggestion,
                                    'confidence': random.randint(85, 99)
                                })
                                
                                st.session_state.chat_history.append(new_message)
                            
                        else:  # Agent
                            agent_responses = [
                                "Thank you for contacting us. I'll help you with your internet issue.",
                                "I understand how frustrating slow internet can be.",
                                "Let me check your account and connection status.",
                                "I can see there might be a signal issue in your area.",
                                "Let's try some troubleshooting steps together.",
                                "Can you please check if all cables are securely connected?",
                                "I'm scheduling a priority technician visit for you.",
                                "Is there anything else I can help you with today?",
                                "I'll send you a follow-up email with the details.",
                                "Thank you for your patience while we resolve this."
                            ]
                            
                            # Avoid duplicate messages by checking recent history
                            recent_messages = [msg['text'] for msg in st.session_state.chat_history[-3:] if msg['speaker'] == 'Agent']
                            available_messages = [msg for msg in agent_responses if msg not in recent_messages]
                            
                            if available_messages:
                                new_message = {
                                    'speaker': 'Agent',
                                    'text': random.choice(available_messages),
                                    'time': datetime.now().strftime("%H:%M:%S"),
                                    'sentiment': 'Professional',
                                    'audio_played': st.session_state.auto_speak  # Set to True if auto-speak is enabled
                                }
                                
                                st.session_state.chat_history.append(new_message)
                        
                        st.session_state.call_duration += random.randint(3, 8)
                        
                        # Show typing indicator for next message
                        if speaker == 'Customer':
                            st.session_state.typing_agent = True
                        else:
                            st.session_state.typing_customer = True
                
                # Clear typing indicators after some time
                if random.random() < 0.7:  # 70% chance to clear typing indicators
                    st.session_state.typing_customer = False
                    st.session_state.typing_agent = False
                
                # Auto-refresh with countdown
                refresh_interval = 3
                placeholder = st.empty()
                for i in range(refresh_interval, 0, -1):
                    placeholder.text(f"🔄 Refreshing in {i} seconds...")
                    time.sleep(1)
                placeholder.empty()
                st.rerun()
            
            # Show last activity
            if st.session_state.chat_history:
                last_msg = st.session_state.chat_history[-1]
                st.markdown(f"**Last activity:** {last_msg['speaker']} at {last_msg['time']}")
            
            # Chat statistics
            st.markdown("### 📈 Chat Statistics")
            if st.session_state.chat_history:
                customer_msgs = len([msg for msg in st.session_state.chat_history if msg['speaker'] == 'Customer'])
                agent_msgs = len([msg for msg in st.session_state.chat_history if msg['speaker'] == 'Agent'])
                
                col_stats1, col_stats2 = st.columns(2)
                with col_stats1:
                    st.metric("👤 Customer", customer_msgs)
                with col_stats2:
                    st.metric("👨‍💼 Agent", agent_msgs)
                
                # Response time simulation
                avg_response_time = random.randint(15, 45)
                st.metric("⏱️ Avg Response Time", f"{avg_response_time}s")
        
        # AI Suggestions Panel
        st.markdown("---")
        st.subheader("🤖 AI Live Suggestions & Voice Analytics")
        
        suggestions_col1, suggestions_col2 = st.columns([2, 1])
        
        with suggestions_col1:
            st.markdown("**Real-time Agent Assistance:**")
            
            # Create suggestions HTML container
            suggestions_html = """
            <div class="suggestion-container">
            """
            
            for suggestion in reversed(st.session_state.suggestions_history[-5:]):  # Show last 5 suggestions
                suggestions_html += f"""
                <div class="suggestion-box">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <strong>🕐 {suggestion['time']}</strong>
                        <span style="color: #28a745; font-weight: bold;">Confidence: {suggestion['confidence']}%</span>
                    </div>
                    <div style="color: #2ca02c;">💡 {suggestion['suggestion']}</div>
                </div>
                """
            
            if not st.session_state.suggestions_history:
                suggestions_html += """
                <div style="text-align: center; color: #6c757d; padding: 20px;">
                    <em>No suggestions yet. Start the conversation to see AI recommendations!</em>
                </div>
                """
            
            suggestions_html += """
            </div>
            """
            
            st.markdown(suggestions_html, unsafe_allow_html=True)
        
        with suggestions_col2:
            st.markdown("**Voice & Quick Actions:**")
            
            # Voice Test Buttons
            st.markdown("**🎤 Voice Testing:**")
            col_test1, col_test2 = st.columns(2)
            
            with col_test1:
                if st.button("Test Customer Voice", use_container_width=True):
                    test_text = "Hello, this is a test of the customer voice."
                    with st.spinner("🔊 Testing customer voice..."):
                        if st.session_state.tts_mode == "offline":
                            tts_manager.speak_offline(test_text, "customer")
                        else:
                            tts_manager.speak_edge_tts(test_text, "customer", use_alt_voice if 'use_alt_voice' in locals() else False)
            
            with col_test2:
                if st.button("Test Agent Voice", use_container_width=True):
                    test_text = "Hello, this is a test of the agent voice."
                    with st.spinner("🔊 Testing agent voice..."):
                        if st.session_state.tts_mode == "offline":
                            tts_manager.speak_offline(test_text, "agent")
                        else:
                            tts_manager.speak_edge_tts(test_text, "agent", use_alt_voice if 'use_alt_voice' in locals() else False)
    
    else:
        # Call Setup Information
        st.markdown("---")
        st.info("""
        ### 🎯 Voice-Enabled Call Simulation Features:
        
        **🔊 Dual Voice Models:**
        - **Customer Voice**: US Neural Voice (natural, conversational)
        - **Agent Voice**: UK Neural Voice (professional, clear)
        
        **🎛️ TTS Options:**
        - **Offline Mode**: pyttsx3 engine (faster, local processing)
        - **Edge-TTS Mode**: Microsoft neural voices (studio quality, free)
        
        **🎪 Interactive Features:**
        - Auto-speak new messages as they appear
        - Manual replay of any message
        - Voice testing for both customer and agent
        - Real-time audio controls (stop/replay)
        - Alternative voice options (male/female)
        
        **📊 Voice Analytics:**
        - Track audio playback coverage
        - Monitor speech synthesis success rate
        - Analyze conversation flow with voice feedback
        
        Click "🟢 Start Call" to begin the voice-enabled simulation!
        """)
        
        # Voice Setup Test
        st.markdown("### 🔧 Pre-Call Voice Setup")
        col_setup1, col_setup2 = st.columns(2)
        
        with col_setup1:
            st.markdown("**Test TTS Engines:**")
            if st.button("🔊 Test Offline TTS"):
                with st.spinner("Testing offline voice..."):
                    success = tts_manager.speak_offline("Testing offline text to speech engine.", "customer")
                    if success:
                        st.success("✅ Offline TTS working!")
                    else:
                        st.error("❌ Offline TTS failed")
        
        with col_setup2:
            if st.button("🌐 Test Edge TTS"):
                with st.spinner("Testing Edge TTS voice..."):
                    success = tts_manager.speak_edge_tts("Testing Microsoft Edge neural text to speech engine.", "agent")
                    if success:
                        st.success("✅ Edge TTS working!")
                    else:
                        st.error("❌ Edge TTS failed")

def training_data_manager_page():
    st.header("📚 Training Data Manager")
    st.markdown("---")
    st.markdown("**Data Ingestion & Preprocessing for AI Model Training**")
    
    # Initialize session state for training data
    if 'training_files' not in st.session_state:
        st.session_state.training_files = [
            {"id": 1, "name": "customer_support_faq.pdf", "type": "PDF", "size": "2.3 MB", "status": "Processed", "date": "2025-01-15"},
            {"id": 2, "name": "product_manual.docx", "type": "DOC", "size": "1.8 MB", "status": "Processing", "date": "2025-01-16"},
            {"id": 3, "name": "chat_transcripts.txt", "type": "TXT", "size": "5.2 MB", "status": "Processed", "date": "2025-01-14"},
        ]
    
    if 'web_sources' not in st.session_state:
        st.session_state.web_sources = [
            {"id": 1, "url": "https://company.com/support", "status": "Active", "last_crawl": "2025-01-16", "pages": 45},
            {"id": 2, "url": "https://help.company.com", "status": "Active", "last_crawl": "2025-01-15", "pages": 23},
            {"id": 3, "url": "https://forum.company.com", "status": "Pending", "last_crawl": "Never", "pages": 0},
        ]
    
    # Tab Navigation
    tab1, tab2, tab3, tab4 = st.tabs(["📁 File Upload", "🌐 Web Sources", "📝 Text Input", "📊 Data Overview"])
    
    # File Upload Tab
    with tab1:
        st.subheader("📁 File Upload & Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Upload Training Files:**")
            uploaded_files = st.file_uploader(
                "Choose files (PDF, DOC, TXT, CSV)",
                type=['pdf', 'doc', 'docx', 'txt', 'csv'],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                for file in uploaded_files:
                    if st.button(f"Process {file.name}"):
                        # Simulate file processing
                        new_file = {
                            "id": len(st.session_state.training_files) + 1,
                            "name": file.name,
                            "type": file.name.split('.')[-1].upper(),
                            "size": f"{file.size / 1024:.1f} KB",
                            "status": "Processing",
                            "date": datetime.now().strftime("%Y-%m-%d")
                        }
                        st.session_state.training_files.append(new_file)
                        st.success(f"Started processing {file.name}")
                        time.sleep(1)
                        st.rerun()
        
        with col2:
            st.markdown("**Processing Options:**")
            chunk_size = st.selectbox("Chunk Size", ["1KB", "5KB", "10KB", "50KB"])
            overlap = st.slider("Overlap %", 0, 50, 10)
            preprocessing = st.multiselect(
                "Preprocessing Steps",
                ["Remove Headers", "Clean Text", "Extract Tables", "OCR Processing"],
                default=["Clean Text"]
            )
        
        # File Management Table
        st.markdown("**Current Training Files:**")
        if st.session_state.training_files:
            df_files = pd.DataFrame(st.session_state.training_files)
            
            # Add action buttons
            for idx, row in df_files.iterrows():
                col_name, col_type, col_size, col_status, col_date, col_actions = st.columns([3, 1, 1, 1, 1, 2])
                
                with col_name:
                    st.write(row['name'])
                with col_type:
                    st.write(row['type'])
                with col_size:
                    st.write(row['size'])
                with col_status:
                    if row['status'] == 'Processed':
                        st.success(row['status'])
                    elif row['status'] == 'Processing':
                        st.warning(row['status'])
                    else:
                        st.error(row['status'])
                with col_date:
                    st.write(row['date'])
                with col_actions:
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button("✏️", key=f"edit_file_{row['id']}"):
                            st.info(f"Edit {row['name']}")
                    with col_delete:
                        if st.button("🗑️", key=f"delete_file_{row['id']}"):
                            st.session_state.training_files = [f for f in st.session_state.training_files if f['id'] != row['id']]
                            st.success(f"Deleted {row['name']}")
                            st.rerun()
    
    # Web Sources Tab
    with tab2:
        st.subheader("🌐 Web Source Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Add New Web Source:**")
            new_url = st.text_input("Website URL", placeholder="https://example.com")
            
            crawl_options = st.columns(3)
            with crawl_options[0]:
                max_depth = st.number_input("Max Depth", min_value=1, max_value=10, value=3)
            with crawl_options[1]:
                max_pages = st.number_input("Max Pages", min_value=1, max_value=1000, value=100)
            with crawl_options[2]:
                crawl_frequency = st.selectbox("Crawl Frequency", ["Daily", "Weekly", "Monthly"])
            
            if st.button("Add Web Source") and new_url:
                new_source = {
                    "id": len(st.session_state.web_sources) + 1,
                    "url": new_url,
                    "status": "Pending",
                    "last_crawl": "Never",
                    "pages": 0
                }
                st.session_state.web_sources.append(new_source)
                st.success(f"Added {new_url} to crawl queue")
                st.rerun()
        
        with col2:
            st.markdown("**Crawl Settings:**")
            respect_robots = st.checkbox("Respect robots.txt", value=True)
            include_images = st.checkbox("Include Images", value=False)
            include_pdfs = st.checkbox("Include PDFs", value=True)
            
            if st.button("🔄 Refresh All Sources"):
                for source in st.session_state.web_sources:
                    if source['status'] == 'Active':
                        source['last_crawl'] = datetime.now().strftime("%Y-%m-%d")
                        source['pages'] = random.randint(10, 100)
                st.success("All sources refreshed!")
                st.rerun()
        
        # Web Sources Table
        st.markdown("**Current Web Sources:**")
        if st.session_state.web_sources:
            for idx, source in enumerate(st.session_state.web_sources):
                col_url, col_status, col_crawl, col_pages, col_actions = st.columns([3, 1, 1, 1, 2])
                
                with col_url:
                    st.write(source['url'])
                with col_status:
                    if source['status'] == 'Active':
                        st.success(source['status'])
                    elif source['status'] == 'Pending':
                        st.warning(source['status'])
                    else:
                        st.error(source['status'])
                with col_crawl:
                    st.write(source['last_crawl'])
                with col_pages:
                    st.write(source['pages'])
                with col_actions:
                    col_crawl_btn, col_delete_btn = st.columns(2)
                    with col_crawl_btn:
                        if st.button("🕷️", key=f"crawl_{source['id']}"):
                            source['status'] = 'Active'
                            source['last_crawl'] = datetime.now().strftime("%Y-%m-%d")
                            source['pages'] = random.randint(5, 50)
                            st.success(f"Started crawling {source['url']}")
                            st.rerun()
                    with col_delete_btn:
                        if st.button("🗑️", key=f"delete_web_{source['id']}"):
                            st.session_state.web_sources = [s for s in st.session_state.web_sources if s['id'] != source['id']]
                            st.success(f"Deleted {source['url']}")
                            st.rerun()
    
    # Text Input Tab
    with tab3:
        st.subheader("📝 Direct Text Input")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Add Training Text:**")
            text_title = st.text_input("Title/Description")
            text_category = st.selectbox("Category", ["FAQ", "Product Info", "Troubleshooting", "General", "Custom"])
            text_content = st.text_area("Content", height=200, placeholder="Enter training text here...")
            
            if st.button("Save Text Entry") and text_content:
                # Simulate saving text entry
                st.success(f"Saved text entry: {text_title}")
                st.info(f"Content length: {len(text_content)} characters")
        
        with col2:
            st.markdown("**Text Processing:**")
            auto_tag = st.checkbox("Auto-tag content", value=True)
            extract_entities = st.checkbox("Extract entities", value=True)
            sentiment_analyze = st.checkbox("Sentiment analysis", value=False)
            
            st.markdown("**Statistics:**")
            st.metric("Total Text Entries", random.randint(150, 300))
            st.metric("Avg. Entry Length", f"{random.randint(200, 800)} chars")
            st.metric("Processing Queue", random.randint(5, 25))
    
    # Data Overview Tab
    with tab4:
        st.subheader("📊 Data Overview & Analytics")
        
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", len(st.session_state.training_files), "↗️ 3")
        with col2:
            st.metric("Web Sources", len(st.session_state.web_sources), "↗️ 1")
        with col3:
            total_pages = sum([s['pages'] for s in st.session_state.web_sources])
            st.metric("Crawled Pages", total_pages, "↗️ 12")
        with col4:
            st.metric("Processing Queue", random.randint(0, 10), "↘️ 2")
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("**File Types Distribution:**")
            file_types = {}
            for file in st.session_state.training_files:
                file_type = file['type']
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            if file_types:
                fig = px.pie(
                    values=list(file_types.values()),
                    names=list(file_types.keys()),
                    title="Training Files by Type"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            st.markdown("**Processing Status:**")
            status_counts = {}
            for file in st.session_state.training_files:
                status = file['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig = px.bar(
                    x=list(status_counts.keys()),
                    y=list(status_counts.values()),
                    title="Files by Processing Status"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Data Quality Metrics
        st.markdown("**Data Quality Metrics:**")
        quality_col1, quality_col2, quality_col3 = st.columns(3)
        
        with quality_col1:
            st.metric("Data Completeness", "94.2%", "↗️ 2.1%")
        with quality_col2:
            st.metric("Data Accuracy", "97.8%", "↗️ 0.5%")
        with quality_col3:
            st.metric("Processing Success Rate", "99.1%", "→ 0.0%")
    
    # Voice Information Panel
    with st.expander("🔊 Available Voice Models"):
        voices_info = tts_manager.get_available_voices()
        
        st.markdown("**🤖 Edge TTS Neural Voices:**")
        col_customer, col_agent = st.columns(2)
        
        with col_customer:
            st.markdown("**👤 Customer Voices:**")
            st.info(f"🔹 {voices_info['edge_tts']['customer']['primary']}")
            st.info(f"🔹 {voices_info['edge_tts']['customer']['alternative']}")
        
        with col_agent:
            st.markdown("**👨‍💼 Agent Voices:**")
            st.info(f"🔹 {voices_info['edge_tts']['agent']['primary']}")
            st.info(f"🔹 {voices_info['edge_tts']['agent']['alternative']}")
        
        if voices_info['offline']:
            st.markdown("**🖥️ System Voices (Offline):**")
            for voice in voices_info['offline'][:5]:  # Show first 5
                st.text(f"• {voice}")
            if len(voices_info['offline']) > 5:
                st.text(f"... and {len(voices_info['offline']) - 5} more")

if __name__ == "__main__":
    main()
