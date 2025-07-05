import streamlit as st
import plotly.express as px
import random

def render_data_overview(training_files):
    """Render the data overview section with metrics and charts"""
    st.subheader("📊 Data Overview & Analytics")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Files", len(training_files), "↗️ 3")
    with col2:
        st.metric("Processing Queue", random.randint(0, 10), "↘️ 2")
    with col3:
        st.metric("Data Completeness", "94.2%", "↗️ 2.1%")
    with col4:
        st.metric("Quality Score", "96.5%", "↗️ 0.8%")
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("**File Types Distribution:**")
        file_types = {}
        for file in training_files:
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
        for file in training_files:
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
        st.metric("Format Consistency", "97.8%", "↗️ 1.2%")
    with quality_col3:
        st.metric("Error Rate", "0.8%", "↘️ 0.3%") 