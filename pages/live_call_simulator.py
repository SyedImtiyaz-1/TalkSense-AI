import streamlit as st
from components.call_control import render_call_control
from components.chat_interface import render_chat_interface

def live_call_simulator_page():
    """Render the live call simulator page"""
    # Initialize session state
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
    
    # Render call control panel
    render_call_control()
    
    if st.session_state.call_active:
        st.markdown("---")
        
        # Connection Status
        st.markdown("""
        <div style="
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        ">
            <span style="
                width: 10px;
                height: 10px;
                background-color: #28a745;
                border-radius: 50%;
                display: inline-block;
            "></span>
            <strong>Call Active</strong> - WebRTC Connected | Audio Quality: HD Voice | Latency: 25ms
        </div>
        """, unsafe_allow_html=True)
        
        # Main chat interface
        main_col, sidebar_col = st.columns([2, 1])
        
        with main_col:
            render_chat_interface()
        
        with sidebar_col:
            st.markdown("### 🌐 Connection Status")
            st.success("🟢 WebRTC Connected")
            st.info("🔊 HD Voice Quality")
            st.info("⚡ Latency: 25ms")
            
            st.markdown("### 🎛️ Voice Settings")
            st.info("👤 Customer: US Neural Voice")
            st.info("👨‍💼 Agent: UK Neural Voice")
            
            st.markdown("### 📊 Call Analytics")
            sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
            for msg in st.session_state.chat_history:
                if msg['speaker'] == 'Customer' and 'sentiment' in msg:
                    sentiment_counts[msg['sentiment']] += 1
            
            for sentiment, count in sentiment_counts.items():
                st.metric(sentiment, count)
    
    else:
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
        
        Click "🟢 Start Call" to begin the voice-enabled simulation!
        """) 