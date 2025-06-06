import os
import base64
import streamlit as st
import pandas as pd
import hashlib
import json
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


def format_message_content(content):
    """整形されたメッセージ内容を返す（dict対応・HTMLエスケープ）"""
    if isinstance(content, dict):
        return f"<pre>{json.dumps(content, indent=2, ensure_ascii=False)}</pre>"
    elif isinstance(content, str) and content.strip().startswith("{") and content.strip().endswith("}"):
        try:
            parsed = json.loads(content)
            return f"<pre>{json.dumps(parsed, indent=2, ensure_ascii=False)}</pre>"
        except Exception:
            return content.replace("<", "&lt;").replace(">", "&gt;")
    return content.replace("<", "&lt;").replace(">", "&gt;")


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
        icon_base64 = get_image_base64(icon_path)
        avatar_html = f'<img src="data:image/png;base64,{icon_base64}" class="avatar" alt="{agent_name}" />'
    else:
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
                        <span class="timestamp">{message_data['Timestamp'].strftime('%H:%M')}</span>
                    </div>
                    <div class="message-text">
                        {format_message_content(message_data['Message'])}
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
    if reverse_order:
        messages_df = messages_df.iloc[::-1]

    with st.container():
        st.markdown(
            """
            <style>
                @media screen and (max-width: 768px) {
                    .main .block-container {
                        padding-left: 10px;
                        padding-right: 10px;
                        padding-top: 1rem;
                    }
                    h1 {
                        font-size: 1.5rem !important;
                    }
                    h2, h3 {
                        font-size: 1.2rem !important;
                    }
                }

                .stApp [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > div:nth-child(2) {
                    overflow-y: auto;
                    max-height: 75vh;
                }

                .message-content-wrapper {
                    display: flex;
                    align-items: flex-start;
                    margin: 10px 0;
                    width: 100%;
                }

                .avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    margin: 0 8px;
                    flex-shrink: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    color: white;
                    font-size: 14px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
                }

                .avatar img {
                    width: 100%;
                    height: 100%;
                    border-radius: 50%;
                    object-fit: cover;
                }

                .message {
                    display: flex;
                    align-items: flex-start;
                    margin-bottom: 15px;
                    width: 100%;
                }

                .message.user {
                    flex-direction: row-reverse;
                }

                .speech-bubble {
                    position: relative;
                    max-width: calc(100% - 60px);
                    padding: 10px 12px;
                    border-radius: 12px;
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
                    text-align: left;
                    font-size: 0.9rem;
                    z-index: 1;
                }

                @media screen and (min-width: 768px) {
                    .speech-bubble {
                        max-width: 70%;
                    }
                }

                .message.agent .speech-bubble {
                    background-color: #0e639c;
                    color: white;
                    margin-left: 2px;
                }

                .message.user .speech-bubble {
                    background-color: #2d2d2d;
                    margin-right: 2px;
                }

                .message.agent .speech-bubble:after {
                    content: "";
                    position: absolute;
                    left: -8px;
                    top: 12px;
                    width: 0;
                    height: 0;
                    border-top: 8px solid transparent;
                    border-bottom: 8px solid transparent;
                    border-right: 8px solid #0e639c;
                }

                .message.user .speech-bubble:after {
                    content: "";
                    position: absolute;
                    right: -8px;
                    top: 12px;
                    width: 0;
                    height: 0;
                    border-top: 8px solid transparent;
                    border-bottom: 8px solid transparent;
                    border-left: 8px solid #2d2d2d;
                }

                .message-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 4px;
                    text-align: left;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    padding-bottom: 4px;
                    font-size: 0.9rem;
                }

                .sender {
                    font-weight: bold;
                    max-width: 70%;
                    text-overflow: ellipsis;
                    overflow: hidden;
                }

                .timestamp {
                    font-size: 0.75em;
                    opacity: 0.7;
                }

                .message-text {
                    text-align: left;
                    display: block;
                    width: 100%;
                    white-space: pre-wrap;
                    line-height: 1.4;
                    overflow-wrap: break-word;
                    word-wrap: break-word;
                    word-break: break-word;
                    font-size: 0.9rem;
                }

                .message-text pre {
                    background-color: rgba(0, 0, 0, 0.2);
                    padding: 10px;
                    border-radius: 8px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                    font-size: 0.85rem;
                    font-family: monospace;
                }

                @media screen and (max-width: 480px) {
                    .message-text {
                        font-size: 0.85rem;
                    }

                    .speech-bubble {
                        padding: 8px 10px;
                    }

                    .avatar {
                        width: 28px;
                        height: 28px;
                        font-size: 12px;
                    }
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        all_messages_html = ""
        for _, row in messages_df.iterrows():
            all_messages_html += render_message(
                message_data=row,
                is_agent=row['Agent'] in selected_agents if selected_agents else False
            )

        st.markdown(
            f'<div class="messages-container">{all_messages_html}</div>',
            unsafe_allow_html=True
        )
