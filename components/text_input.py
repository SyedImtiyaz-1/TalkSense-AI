import streamlit as st
import random

def render_text_input():
    """Render the text input section for direct text entry"""
    st.subheader("📝 Direct Text Input")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Add Training Text:**")
        text_title = st.text_input("Title/Description")
        text_category = st.selectbox(
            "Category",
            ["FAQ", "Product Info", "Troubleshooting", "General", "Custom"]
        )
        text_content = st.text_area(
            "Content",
            height=200,
            placeholder="Enter training text here..."
        )
        
        if st.button("Save Text Entry") and text_content:
            # TODO: Implement actual text saving logic
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