import streamlit as st
import os
from config.settings import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE
)
from pages.training_data_manager import training_data_manager_page
from pages.live_call_simulator import live_call_simulator_page

# Set page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# Load custom CSS
def load_css():
    try:
        css_file_path = os.path.join(os.path.dirname(__file__), "static/css/style.css")
        with open(css_file_path, encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ CSS file not found. Using default styling.")
        pass

def main():
    # Load CSS
    load_css()
    
    # Title and description
    # st.title("🎯 AI Call Center - Live Insights")
    # st.markdown("---")
    st.title("**AI-Driven Live Call Insights**")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🎯 Live Call Simulator", "📚 Training Data Manager"]
    )
    
    if page == "🎯 Live Call Simulator":
        live_call_simulator_page()
    elif page == "📚 Training Data Manager":
        training_data_manager_page()

if __name__ == "__main__":
    main()
