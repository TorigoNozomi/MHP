import streamlit as st
import hashlib
from datetime import datetime
import os
import re

def get_color_for_agent(agent: str) -> str:
    """Generate a consistent color for an agent based on their name."""
    hash_obj = hashlib.md5(agent.encode())
    hash_hex = hash_obj.hexdigest()
    return f"#{hash_hex[:6]}"

def get_agent_icon(agent: str) -> str:
    """Get the URL for an agent's icon image."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    icon_path = os.path.join(static_dir, f"{agent}.png")
    if os.path.exists(icon_path):
        return f"static/{agent}.png"
    return ""

def format_race_prediction(message: str) -> str:
    """Format race prediction messages with proper spacing and alignment."""
    # Compress multiple newlines into a single newline
    message = re.sub(r'\n\s*\n+', '\n\n', message)
    
    # Fix table alignment by ensuring cell contents are properly spaced
    message = re.sub(r'\|\s*([^|\n]*?)\s*\|', r'| \1 |', message)
    
    # Ensure proper spacing around headers
    message = re.sub(r'(\n\s*#{1,6}\s*[^\n]+)', r'\n\1\n', message)
    
    # Fix list formatting by ensuring proper spacing
    message = re.sub(r'(\n\s*[*-]\s+[^\n]+)(\n[^*\n-])', r'\1\n\2', message)
    
    return message.strip()

def render_message(timestamp: datetime, agent: str, message: str, align_right: bool = False):
    """
    Render a single message in the chat interface.
    
    Args:
        timestamp (datetime): Message timestamp
        agent (str): Name of the message sender
        message (str): Content of the message
        align_right (bool, optional): Whether to align the message to the right
    """
    container_class = "message-container right" if align_right else "message-container"
    icon_url = get_agent_icon(agent)
    
    # Format race prediction messages from WHITEBOARD
    if agent == "WHITEBOARD":
        message = format_race_prediction(message)
    
    with st.container():
        st.markdown(
            f"""
            <div class="{container_class}">
                <div class="avatar" style="background-color: {get_color_for_agent(agent)}">
                    {f'<img src="{icon_url}" alt="{agent}" />' if icon_url else agent[0].upper()}
                </div>
                <div class="message-content" style="text-align: left; align-self: flex-start;">
                    <div class="agent-name" style="text-align: left;">{agent}</div>
                    <div class="message-text" style="text-align: left; vertical-align: top; white-space: pre-wrap;">{message}</div>
                    <div class="timestamp">{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )