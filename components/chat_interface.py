import streamlit as st
import random
from datetime import datetime
from services.tts_service import tts_service

def render_chat_interface():
    """Render the chat interface with messages and controls"""
    st.subheader("💬 Live Conversation")
    
    # Display messages
    for msg in st.session_state.chat_history:
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
                </div>
                """, unsafe_allow_html=True)
    
    # Chat controls
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Sample messages
    customer_messages = [
        "Hi, I'm having trouble with my internet connection.",
        "It's been slow for the past three days.",
        "I've already tried restarting the router.",
        "The speed test shows only 10 Mbps instead of 100.",
        "This is really frustrating. I work from home."
    ]
    
    agent_responses = [
        "Thank you for contacting us. I'll help you with your internet issue.",
        "I understand how frustrating slow internet can be.",
        "Let me check your account and connection status.",
        "I can see there might be a signal issue in your area.",
        "Let's try some troubleshooting steps together."
    ]
    
    with col1:
        if st.button("👤 Customer Speaks", type="primary"):
            if customer_messages:
                msg = random.choice(customer_messages)
                sentiment = random.choice(["Positive", "Neutral", "Negative"])
                current_time = datetime.now().strftime("%H:%M:%S")
                
                new_message = {
                    'speaker': 'Customer',
                    'text': msg,
                    'time': current_time,
                    'sentiment': sentiment,
                    'audio_played': False
                }
                st.session_state.chat_history.append(new_message)
                
                if st.session_state.auto_speak:
                    with st.spinner("🔊 Speaking..."):
                        if st.session_state.tts_mode == "offline":
                            success = tts_service.speak_offline(msg, "customer")
                        else:
                            success = tts_service.speak_edge_tts(msg, "customer")
                        
                        if success:
                            st.session_state.chat_history[-1]['audio_played'] = True
                
                st.session_state.call_duration += random.randint(5, 15)
                st.rerun()
    
    with col2:
        if st.button("👨‍💼 Agent Responds", type="primary"):
            if agent_responses:
                msg = random.choice(agent_responses)
                current_time = datetime.now().strftime("%H:%M:%S")
                
                new_message = {
                    'speaker': 'Agent',
                    'text': msg,
                    'time': current_time,
                    'sentiment': 'Professional',
                    'audio_played': False
                }
                st.session_state.chat_history.append(new_message)
                
                if st.session_state.auto_speak:
                    with st.spinner("🔊 Speaking..."):
                        if st.session_state.tts_mode == "offline":
                            success = tts_service.speak_offline(msg, "agent")
                        else:
                            success = tts_service.speak_edge_tts(msg, "agent")
                        
                        if success:
                            st.session_state.chat_history[-1]['audio_played'] = True
                
                st.session_state.call_duration += random.randint(3, 10)
                st.rerun()
    
    with col3:
        if st.button("🔊 Replay Last Customer"):
            customer_msgs = [msg for msg in st.session_state.chat_history if msg['speaker'] == 'Customer']
            if customer_msgs:
                last_msg = customer_msgs[-1]['text']
                with st.spinner("🔊 Replaying..."):
                    if st.session_state.tts_mode == "offline":
                        tts_service.speak_offline(last_msg, "customer")
                    else:
                        tts_service.speak_edge_tts(last_msg, "customer")
    
    with col4:
        if st.button("🔊 Replay Last Agent"):
            agent_msgs = [msg for msg in st.session_state.chat_history if msg['speaker'] == 'Agent']
            if agent_msgs:
                last_msg = agent_msgs[-1]['text']
                with st.spinner("🔊 Replaying..."):
                    if st.session_state.tts_mode == "offline":
                        tts_service.speak_offline(last_msg, "agent")
                    else:
                        tts_service.speak_edge_tts(last_msg, "agent")
    
    with col5:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.suggestions_history = []
            st.success("Chat cleared!")
            st.rerun() 