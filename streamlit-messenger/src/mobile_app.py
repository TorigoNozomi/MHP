import streamlit as st
import pandas as pd
from datetime import datetime
from utils.csv_parser import load_messages, filter_messages
from utils.thread_parser import get_race_threads
from components.message_list import render_message_list
import os

# Set page config for mobile-friendly layout
st.set_page_config(
    page_title="Race Chat",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed on mobile
)

# Add custom CSS for mobile responsiveness
st.markdown("""
<style>
/* Mobile-friendly tweaks */
@media screen and (max-width: 768px) {
    /* Make sidebar narrower on mobile */
    [data-testid="stSidebar"] {
        width: 16rem !important;
    }
    
    /* Smaller padding in main content */
    .main .block-container {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        max-width: 100%;
    }
    
    /* Smaller margins for info boxes */
    .stAlert {
        padding: 0.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Adjust filter expander padding */
    .streamlit-expanderHeader {
        padding: 0.5rem !important;
    }
    
    /* Smaller text for info box */
    .stInfo p {
        font-size: 0.8rem !important;
    }
}

/* Fix the race-info box in sidebar */
.race-info {
    font-size: 0.9rem;
    padding: 10px;
    margin: 10px 0;
}

/* Title styling for mobile */
@media screen and (max-width: 768px) {
    h1 {
        font-size: 1.5rem !important;
        margin-top: 0.5rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Get all race threads
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
threads = get_race_threads(data_dir)

# Sidebar for race selection - simpler on mobile
with st.sidebar:
    st.header("Race Selection")
    
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
        
        # Simplified race info for mobile
        st.markdown('<div class="race-info">', unsafe_allow_html=True)
        st.markdown(f"""
            ### Race Details
            **Date:** {selected_thread.date.strftime('%Y-%m-%d')}  
            **Racecourse:** {selected_thread.racecourse}  
            **Race:** {selected_thread.race_number}R
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# Main content area
if selected_thread:
    # Add a mobile-friendly toggle for sidebar
    col1, col2 = st.columns([3, 1])
    with col1:
        # Race name as thread title
        st.title(f"🏇 {selected_thread.racecourse} {selected_thread.race_number}R")
    
    with col2:
        # Mobile-friendly sidebar toggle button
        if st.button("📋 Race Info"):
            # This is just a button to open sidebar on mobile
            pass
    
    try:
        # Load messages
        df = load_messages(selected_thread.full_path)
        
        # Get unique agents
        agents = sorted(df['Agent'].unique())
        
        # Simplified filtering controls
        with st.expander("Filters", expanded=False):
            # Simple columns layout for filters
            selected_agents = st.multiselect(
                "Participants",
                agents,
                default=agents
            )
            
            # Two columns for search and order
            fc1, fc2 = st.columns([3, 1])
            with fc1:
                search_query = st.text_input("Search", placeholder="Enter search terms...")
            with fc2:
                reverse_order = st.checkbox("Newest First")
        
        # Apply filters
        filtered_df = df[df['Agent'].isin(selected_agents)]
        
        if search_query:
            filtered_df = filtered_df[
                filtered_df['Message'].str.contains(search_query, case=False, na=False)
            ]
        
        # Smaller info message
        st.info(f"{len(filtered_df)} of {len(df)} messages")
        
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