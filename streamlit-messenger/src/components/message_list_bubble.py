import os
import base64
import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

def generate_color_from_string(text):
    """Generate a consistent color based on text input."""
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    hue = int(hash_hex[:3], 16) % 360
    return f"hsl({hue}, 70%, 40%)"

def get_initials(name):
    """Get initials from name (up to 2 characters)."""
    words = name.split()
    initials = ''.join(word[0].upper() for word in words if word)
    return initials[:2]

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def render_message(message_data, is_agent):
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    agent_name = message_data['Agent']
    
    # Try to get agent-specific icon
    icon_path = None
    if is_agent:
        specific_icon = os.path.join(assets_dir, f"{agent_name}.png")
        default_icon = os.path.join(assets_dir, "agent_icon.png")
        icon_path = specific_icon if os.path.exists(specific_icon) else default_icon
    else:
        user_icon = os.path.join(assets_dir, "user_icon.png")
        icon_path = user_icon if os.path.exists(user_icon) else None
        
    message_class = "message agent" if is_agent else "message user"
    
    # Generate avatar HTML
    if icon_path and os.path.exists(icon_path):
        # Use image icon
        icon_base64 = get_image_base64(icon_path)
        avatar_html = f'<img src="data:image/png;base64,{icon_base64}" class="avatar" alt="{agent_name}" />'
    else:
        # Use initials with background color
        initials = get_initials(agent_name if is_agent else "User")
        bg_color = generate_color_from_string(agent_name if is_agent else "User")
        avatar_html = f'<div class="avatar" style="background-color: {bg_color};">{initials}</div>'
    
    # Format message with speech bubble
    return f"""
        <div class="{message_class}">
            <div class="message-content-wrapper">
                {avatar_html}
                <div class="message-content speech-bubble">
                    <div class="message-header">
                        <span class="sender">{agent_name if is_agent else 'User'}</span>
                        <span class="timestamp">{message_data['Timestamp'].strftime('%Y-%m-%d %H:%M')}</span>
                    </div>
                    <div class="message-text">
                        {message_data['Message']}
                    </div>
                </div>
            </div>
        </div>
    """

def render_message_list(
    messages_df: pd.DataFrame,
    selected_agents: list[str] = None,
    start_date: datetime = None,
    end_date: datetime = None,
    search_query: str = None,
    reverse_order: bool = False
):
    """
    Render a list of messages with optional filtering.
    
    Args:
        messages_df (pd.DataFrame): DataFrame containing messages
        selected_agents (list[str], optional): List of agents to display messages from
        start_date (datetime, optional): Start date for filtering messages
        end_date (datetime, optional): End date for filtering messages
        search_query (str, optional): Text to search for in messages
        reverse_order (bool, optional): Whether to display messages in reverse chronological order
    """
    if reverse_order:
        messages_df = messages_df.iloc[::-1]
    
    # Create a container for the messages with custom CSS for scrolling
    with st.container():
        st.markdown(
            """
            <style>
                /* Message container styling */
                .stApp [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > div:nth-child(2) {
                    overflow-y: auto;
                    max-height: 75vh;
                }
                
                /* Message wrapper styling */
                .message-content-wrapper {
                    display: flex;
                    align-items: flex-start;
                    margin: 15px 0;
                }
                
                /* Avatar styling */
                .avatar {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    margin: 0 12px;
                    flex-shrink: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    color: white;
                    font-size: 16px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                }
                
                .avatar img {
                    width: 100%;
                    height: 100%;
                    border-radius: 50%;
                    object-fit: cover;
                }
                
                /* Message styling */
                .message {
                    display: flex;
                    align-items: flex-start;
                    margin-bottom: 20px;
                    width: 100%;
                    max-width: 90%;
                }
                
                .message.user {
                    flex-direction: row-reverse;
                    margin-left: auto;
                }
                
                /* Speech bubble styling */
                .speech-bubble {
                    position: relative;
                    max-width: 70%;
                    padding: 12px 15px;
                    border-radius: 10px;
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
                    text-align: left;
                }
                
                .message.agent .speech-bubble {
                    background-color: #0e639c;
                    color: white;
                }
                
                .message.agent .speech-bubble:before {
                    content: "";
                    position: absolute;
                    left: -8px;
                    top: 15px;
                    border-width: 8px 8px 8px 0;
                    border-style: solid;
                    border-color: transparent #0e639c transparent transparent;
                }
                
                .message.user .speech-bubble:before {
                    content: "";
                    position: absolute;
                    right: -8px;
                    top: 15px;
                    border-width: 8px 0 8px 8px;
                    border-style: solid;
                    border-color: transparent transparent transparent #2d2d2d;
                }
                
                /* Message header styling */
                .message-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 5px;
                    text-align: left;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    padding-bottom: 5px;
                }
                
                .sender {
                    font-weight: bold;
                }
                
                .timestamp {
                    font-size: 0.8em;
                    opacity: 0.7;
                }
                
                /* Message text styling */
                .message-text {
                    text-align: left;
                    display: block;
                    width: 100%;
                    white-space: pre-wrap;
                    line-height: 1.5;
                    overflow-wrap: break-word;
                    word-wrap: break-word;
                    word-break: break-word;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Render each message
        for _, row in messages_df.iterrows():
            st.markdown(
                render_message(
                    message_data=row,
                    is_agent=row['Agent'] in selected_agents if selected_agents else False
                ),
                unsafe_allow_html=True
            )