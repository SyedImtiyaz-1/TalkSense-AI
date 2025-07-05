import streamlit as st
from services.tts_service import tts_service

def render_call_control():
    """Render the call control panel"""
    st.subheader("📞 Call Control")
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
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
                    tts_service.stop_audio()
                    st.rerun()
            with col_stop:
                if st.button("⏹️ Stop Audio"):
                    tts_service.stop_audio()
    
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