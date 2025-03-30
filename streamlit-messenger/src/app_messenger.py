import streamlit as st
import pandas as pd
from datetime import datetime
from utils.csv_parser import load_messages, filter_messages
from utils.thread_parser import get_race_threads
from components.message_list_bubble import render_message_list
import os

# Set page config
st.set_page_config(
    page_title="Race Analysis Chat",
    page_icon="🏇",
    layout="wide"  # Use wide layout for messenger-like UI
)

# Get all race threads
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
threads = get_race_threads(data_dir)

# Sidebar for race selection
with st.sidebar:
    st.header("Select Race Analysis")
    
    if not threads:
        st.error("No race analysis files found")
        selected_thread = None
    else:
        # Create a mapping from display name to thread object
        thread_options = {thread.display_name: thread for thread in threads}
        selected_thread_name = st.selectbox(
            "Choose a race:",
            options=list(thread_options.keys()),
            index=0
        )
        selected_thread = thread_options[selected_thread_name]
        
        # Display selected race details in the sidebar
        st.markdown('<div class="race-info">', unsafe_allow_html=True)
        st.markdown(f"""
            ### Current Race Details
            - **Date:** {selected_thread.date.strftime('%Y-%m-%d')}
            - **Racecourse:** {selected_thread.racecourse}
            - **Race Number:** {selected_thread.race_number}
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# Main content area
if selected_thread:
    # Race name as thread title
    st.title(f"🏇 {selected_thread.racecourse} {selected_thread.race_number}R Analysis")
    
    try:
        # Load messages
        df = load_messages(selected_thread.full_path)
        
        # Get unique agents
        agents = sorted(df['Agent'].unique())
        
        # Simple filtering controls
        with st.expander("Message Filters", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_agents = st.multiselect(
                    "Select Participants",
                    agents,
                    default=agents
                )
                
                search_query = st.text_input("Search Messages")
            
            with col2:
                reverse_order = st.checkbox("Show Newest First")
        
        # Apply filters
        filtered_df = df[df['Agent'].isin(selected_agents)]
        
        if search_query:
            filtered_df = filtered_df[
                filtered_df['Message'].str.contains(search_query, case=False, na=False)
            ]
        
        # Display message count
        st.info(f"Showing {len(filtered_df)} of {len(df)} messages")
        
        # Render messages with speech bubbles and icons
        render_message_list(
            filtered_df,
            selected_agents=selected_agents,
            reverse_order=reverse_order
        )
        
    except Exception as e:
        st.error(f"Error loading messages: {str(e)}")
else:
    st.title("🏇 Race Analysis Chat")
    st.info("Please select a race from the sidebar to view the analysis.")