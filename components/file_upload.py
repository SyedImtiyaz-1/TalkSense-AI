import streamlit as st
from services.s3_service import s3_service
import pandas as pd
from datetime import datetime

class FileUpload:
    def render(self):
        st.subheader("File Upload")
        
        # File uploader
        uploaded_file = st.file_uploader("Upload your training data", type=['txt', 'csv', 'pdf'])
        
        if uploaded_file is not None:
            try:
                # Upload to S3
                success, message = s3_service.upload_file(uploaded_file, uploaded_file.name)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"Error uploading file: {e}")

        # Display uploaded files
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
                
                # Create the table header
                cols = st.columns([1, 3, 2, 3, 2])
                cols[0].write('#')
                cols[1].write('**Key**')
                cols[2].write('**Size**')
                cols[3].write('**LastModified**')
                cols[4].write('**Actions**')
                
                # Create table rows
                for _, row in df.iterrows():
                    cols = st.columns([1, 3, 2, 3, 2])
                    cols[0].write(row['Index'])
                    cols[1].write(row['Key'])
                    cols[2].write(row['Size'])
                    cols[3].write(row['LastModified'])
                    
                    # Delete button
                    if cols[4].button('🗑️ Delete', key=f"delete_{row['Index']}"):
                        success, message = s3_service.delete_file(row['Actions'])
                        if success:
                            st.success(f"Successfully deleted {row['Key']}")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete {row['Key']}: {message}")
        else:
            st.info("No files uploaded yet.") 