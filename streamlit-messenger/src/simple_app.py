import streamlit as st
import pandas as pd
from datetime import datetime
from utils.csv_parser import load_messages, filter_messages
from utils.thread_parser import get_race_threads
from components.message_list import render_message_list
import os

# Set page config
st.set_page_config(
    page_title="Simple Race Chat",
    page_icon="🏇",
    layout="centered"
)

# Simple header
st.title("🏇 Race Analysis Chat")

# Get all race threads
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
threads = get_race_threads(data_dir)

# Simple race selection
if not threads:
    st.error("No race analysis files found")
else:
    # Create a mapping from display name to thread object
    thread_options = {thread.display_name: thread for thread in threads}
    selected_thread_name = st.selectbox(
        "Choose a race:",
        options=list(thread_options.keys()),
        index=0
    )
    selected_thread = thread_options[selected_thread_name]
    
    # Display basic race info in a simple format
    st.markdown("### Race Details")
    st.write(f"**Date:** {selected_thread.date.strftime('%Y-%m-%d')}")
    st.write(f"**Racecourse:** {selected_thread.racecourse}")
    st.write(f"**Race Number:** {selected_thread.race_number}")
    
    try:
        # Load messages
        df = load_messages(selected_thread.full_path)
        
        # Simple filtering options
        with st.expander("Message Filters"):
            # Get unique agents
            agents = sorted(df['Agent'].unique())
            selected_agents = st.multiselect(
                "Select Participants",
                agents,
                default=agents
            )
            
            # Simple search
            search_query = st.text_input("Search Messages")
            
            # Ordering option
            reverse_order = st.checkbox("Show Newest First")
        
        # Apply filters
        filtered_df = df[df['Agent'].isin(selected_agents)]
        
        if search_query:
            filtered_df = filtered_df[
                filtered_df['Message'].str.contains(search_query, case=False, na=False)
            ]
        
        # Display message count
        st.info(f"Showing {len(filtered_df)} of {len(df)} messages")
        
        # Render messages with simplified component
        render_message_list(
            filtered_df,
            selected_agents=selected_agents,
            reverse_order=reverse_order
        )
        
    except Exception as e:
        st.error(f"Error loading messages: {str(e)}")