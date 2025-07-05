import streamlit as st
from services.s3_service import s3_service
import pandas as pd
import plotly.express as px
import numpy as np

def training_data_manager_page():
    st.title("Training Data Manager")
    
    # Create tabs for different input methods
    tab1, tab2, tab3, tab4 = st.tabs(["📁 File Upload", "📝 Input Data", "🌐 Web Source", "📊 Data Analysis"])
    
    with tab1:
        st.header("Upload Training Data")
        uploaded_file = st.file_uploader("Upload your training data", type=['txt', 'csv', 'pdf'])
        
        if uploaded_file is not None:
            try:
                # Show file info
                st.info(f"File: {uploaded_file.name}")
                file_details = {
                    "Filename": uploaded_file.name,
                    "FileType": uploaded_file.type,
                    "FileSize": f"{uploaded_file.size / 1024:.2f} KB"
                }
                st.json(file_details)
                
                # Analysis options
                st.subheader("Analysis Options")
                col1, col2 = st.columns(2)
                with col1:
                    analysis_type = st.selectbox(
                        "Select Analysis Type",
                        ["Basic Analysis", "Detailed Analysis", "Custom Analysis"]
                    )
                with col2:
                    if analysis_type == "Custom Analysis":
                        custom_params = st.text_input("Custom Parameters")
                
                # Upload and Analyze buttons side by side
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Upload to Storage", type="primary"):
                        success, message = s3_service.upload_file(uploaded_file, uploaded_file.name)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                with col2:
                    if st.button("Run Analysis", type="secondary"):
                        with st.spinner('Running analysis...'):
                            st.info("Analysis in progress... This may take a few moments.")
                            # Add your analysis logic here
                            st.success("Analysis completed!")
                            
            except Exception as e:
                st.error(f"Error processing file: {e}")

    with tab2:
        st.header("Input Training Data")
        
        # Input method selection
        input_method = st.radio(
            "Select Input Method",
            ["Single Entry", "Batch Entry"],
            horizontal=True
        )
        
        if input_method == "Single Entry":
            # Single entry form
            with st.form("single_entry_form"):
                st.subheader("Enter Training Data")
                
                col1, col2 = st.columns(2)
                with col1:
                    category = st.selectbox(
                        "Category",
                        ["Customer Service", "Technical Support", "Sales", "Other"]
                    )
                    
                with col2:
                    priority = st.select_slider(
                        "Priority",
                        options=["Low", "Medium", "High", "Critical"]
                    )
                
                # Input fields
                user_input = st.text_area("User Input", height=100)
                expected_response = st.text_area("Expected Response", height=100)
                
                # Additional metadata
                col1, col2 = st.columns(2)
                with col1:
                    tags = st.multiselect(
                        "Tags",
                        ["Complaint", "Query", "Feedback", "Request", "Technical", "Billing"]
                    )
                with col2:
                    language = st.selectbox(
                        "Language",
                        ["English", "Spanish", "French", "German", "Other"]
                    )
                
                # Notes
                notes = st.text_input("Additional Notes")
                
                # Submit button
                submitted = st.form_submit_button("Add Entry")
                if submitted:
                    st.success("Entry added successfully!")
                    
        else:  # Batch Entry
            st.subheader("Batch Entry")
            st.info("Enter multiple training examples, one per line")
            
            # Template download
            st.download_button(
                "Download Template",
                "Category,Priority,User Input,Expected Response,Tags,Language,Notes\n",
                "training_data_template.csv",
                "text/csv"
            )
            
            # Batch input
            batch_input = st.text_area(
                "Paste your data here (CSV format)",
                height=200,
                help="Format: Category,Priority,Input,Response,Tags,Language,Notes"
            )
            
            if st.button("Process Batch"):
                if batch_input:
                    st.success("Batch data processed successfully!")
                else:
                    st.error("Please enter some data to process")

        # Analysis Section
        st.markdown("---")
        st.subheader("Analysis Tools")
        
        analysis_type = st.selectbox(
            "Choose Analysis Type",
            [
                "Content Analysis",
                "Response Quality Check",
                "Language Analysis",
                "Sentiment Analysis",
                "Custom Analysis"
            ]
        )
        
        # Analysis parameters based on type
        if analysis_type == "Content Analysis":
            st.checkbox("Check for completeness")
            st.checkbox("Validate formatting")
            st.checkbox("Identify key topics")
            
        elif analysis_type == "Response Quality Check":
            st.slider("Minimum response length", 0, 500, 50)
            st.checkbox("Check grammar")
            st.checkbox("Check tone")
            
        elif analysis_type == "Language Analysis":
            st.multiselect(
                "Select language features to analyze",
                ["Grammar", "Vocabulary", "Sentiment", "Formality"]
            )
            
        elif analysis_type == "Sentiment Analysis":
            st.radio(
                "Sentiment granularity",
                ["Basic (Positive/Negative)", "Detailed (5-point scale)"]
            )
            
        elif analysis_type == "Custom Analysis":
            st.text_area("Enter custom analysis parameters")
        
        # Run analysis button
        if st.button("Run Analysis", type="primary"):
            with st.spinner("Running analysis..."):
                # Placeholder for analysis results
                st.info("Analysis in progress...")
                
                # Create tabs for different result views
                result_tab1, result_tab2, result_tab3 = st.tabs(["Summary", "Details", "Visualization"])
                
                with result_tab1:
                    st.write("Analysis Summary")
                    st.metric("Quality Score", "85%")
                    
                with result_tab2:
                    st.write("Detailed Analysis")
                    st.json({
                        "total_entries": 10,
                        "quality_metrics": {
                            "completeness": 0.9,
                            "accuracy": 0.85,
                            "consistency": 0.88
                        }
                    })
                    
                with result_tab3:
                    st.write("Analysis Visualization")
                    st.info("Visualizations will appear here")
                
                st.success("Analysis completed!")
    
    with tab3:
        st.header("Add Web Source")
        
        # Web source input
        web_url = st.text_input("Enter Web URL", placeholder="https://example.com/data")
        source_name = st.text_input("Source Name", placeholder="Company Blog")
        
        # Source type selection
        source_type = st.selectbox(
            "Source Type",
            ["Website", "API", "RSS Feed", "Other"]
        )
        
        # Additional options based on source type
        if source_type == "API":
            st.text_input("API Key (if required)", type="password")
            st.selectbox("Authentication Type", ["None", "Basic", "Bearer Token", "OAuth"])
        
        # Fetch frequency
        st.select_slider(
            "Fetch Frequency",
            options=["Once", "Hourly", "Daily", "Weekly", "Monthly"]
        )
        
        if st.button("Add Web Source", type="primary"):
            st.info("Adding web source...")
            # Add your web source processing logic here
            st.success("Web source added successfully!")

    with tab4:
        st.header("Data Analysis Dashboard")
        
        # Data source selection
        data_source = st.selectbox(
            "Select Data Source",
            ["Uploaded Files", "Input Data", "Web Sources", "All Sources"]
        )
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
            
        # Analysis type selection
        analysis_type = st.radio(
            "Analysis Type",
            ["Overview", "Detailed Analysis", "Custom Metrics"],
            horizontal=True
        )
        
        # Create placeholder data for demonstration
        if st.button("Generate Analysis"):
            with st.spinner("Analyzing data..."):
                # Overview Section
                st.subheader("Data Overview")
                metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                
                with metrics_col1:
                    st.metric("Total Entries", "1,234")
                with metrics_col2:
                    st.metric("Avg. Response Time", "2.5s", delta="-0.5s")
                with metrics_col3:
                    st.metric("Quality Score", "85%", delta="3%")
                with metrics_col4:
                    st.metric("Completion Rate", "92%", delta="-1%")
                
                # Visualization Section
                st.subheader("Data Visualization")
                viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Trends", "Distribution", "Patterns"])
                
                with viz_tab1:
                    # Sample data for trend visualization
                    dates = pd.date_range(start='2024-01-01', end='2024-03-01', freq='D')
                    values = np.random.normal(100, 15, len(dates))
                    trend_data = pd.DataFrame({'Date': dates, 'Value': values})
                    
                    fig = px.line(trend_data, x='Date', y='Value', title='Training Data Trends')
                    st.plotly_chart(fig, use_container_width=True)
                
                with viz_tab2:
                    # Sample data for distribution
                    categories = ['Customer Service', 'Technical', 'Sales', 'Other']
                    values = np.random.randint(50, 200, len(categories))
                    dist_data = pd.DataFrame({'Category': categories, 'Count': values})
                    
                    fig = px.bar(dist_data, x='Category', y='Count', title='Data Distribution by Category')
                    st.plotly_chart(fig, use_container_width=True)
                
                with viz_tab3:
                    # Sample data for pattern analysis
                    pattern_data = pd.DataFrame({
                        'x': np.random.normal(0, 1, 100),
                        'y': np.random.normal(0, 1, 100)
                    })
                    
                    fig = px.scatter(pattern_data, x='x', y='y', title='Pattern Analysis')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Insights Section
                st.subheader("Key Insights")
                
                # Display insights in an expandable container
                with st.expander("View Detailed Insights"):
                    st.markdown("""
                    - **Quality Metrics**
                        - High completion rate across all categories
                        - Improved response accuracy in technical queries
                        
                    - **Trend Analysis**
                        - Steady increase in data volume
                        - Seasonal patterns detected in customer inquiries
                        
                    - **Recommendations**
                        - Focus on improving response time in peak hours
                        - Consider adding more technical training data
                    """)
                
                # Export options
                st.subheader("Export Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download Full Report",
                        data="Sample report data",
                        file_name="analysis_report.pdf",
                        mime="application/pdf"
                    )
                with col2:
                    st.download_button(
                        "Export Raw Data",
                        data="Sample raw data",
                        file_name="raw_data.csv",
                        mime="text/csv"
                    )

    # Display existing files section
    st.markdown("---")
    st.header("Existing Training Data")
    files = s3_service.list_files()
    if files:
        # Create DataFrame with the exact columns from the image
        data = []
        for idx, f in enumerate(files):
            file_name = f['Key'].split('/')[-1]
            if not file_name:  # Skip if it's just the prefix
                continue
            data.append({
                'Index': idx,
                'Key': file_name,
                'Size': f['Size'],
                'LastModified': f['LastModified'].strftime('%Y-%m-%d %H:%M:%S+00:00'),
                'Actions': f['Key']  # Store full key for deletion
            })
        
        if data:
            df = pd.DataFrame(data)
            
            # Create the table header with improved styling
            st.markdown("""
                <style>
                .stDataFrame {
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Create table with better styling
            cols = st.columns([1, 3, 2, 3, 2])
            cols[0].markdown("**#**")
            cols[1].markdown("**File Name**")
            cols[2].markdown("**Size**")
            cols[3].markdown("**Last Modified**")
            cols[4].markdown("**Actions**")
            
            # Create table rows with alternating colors
            for idx, row in df.iterrows():
                cols = st.columns([1, 3, 2, 3, 2])
                cols[0].write(row['Index'])
                cols[1].write(row['Key'])
                cols[2].write(f"{row['Size']/1024:.2f} KB")
                cols[3].write(row['LastModified'])
                
                # Action buttons
                action_col = cols[4].container()
                col1, col2 = action_col.columns(2)
                
                # Delete button
                if col2.button('🗑️ Delete', key=f"delete_{row['Index']}"):
                    success, message = s3_service.delete_file(row['Actions'])
                    if success:
                        st.success(f"Successfully deleted {row['Key']}")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete {row['Key']}: {message}")
    else:
        st.info("No files uploaded yet.") 