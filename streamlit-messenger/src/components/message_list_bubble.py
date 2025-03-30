import os
import base64
import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime


def generate_color_from_string(text):
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    hue = int(hash_hex[:3], 16) % 360
    return f"hsl({hue}, 70%, 40%)"


def get_initials(name):
    words = name.split()
    initials = ''.join(word[0].upper() for word in words if word)
    return initials[:2]


def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def format_message_content(content):
    """辞書型やJSON文字列を整形して prediction 部分のみ安全に表示"""
    try:
        if isinstance(content, dict):
            return content.get("prediction", json.dumps(content, ensure_ascii=False))
        elif isinstance(content, str):
            stripped = content.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                try:
                    parsed = eval(stripped)
                    if isinstance(parsed, dict):
                        return parsed.get("prediction", json.dumps(parsed, ensure_ascii=False))
                except Exception:
                    pass
            return content.replace("<", "&lt;").replace(">", "&gt;")
    except Exception:
        return str(content).replace("<", "&lt;").replace(">", "&gt;")


def render_message(message_data, is_agent):
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    agent_name = message_data['Agent']

    icon_path = None
    if is_agent:
        specific_icon = os.path.join(assets_dir, f"{agent_name}.png")
        default_icon = os.path.join(assets_dir, "agent_icon.png")
        icon_path = specific_icon if os.path.exists(specific_icon) else default_icon
    else:
        user_icon = os.path.join(assets_dir, "user_icon.png")
        icon_path = user_icon if os.path.exists(user_icon) else None

    message_class = "message agent" if is_agent else "message user"

    if icon_path and os.path.exists(icon_path):
        icon_base64 = get_image_base64(icon_path)
        avatar_html = f'<img src="data:image/png;base64,{icon_base64}" class="avatar" alt="{agent_name}" />'
    else:
        initials = get_initials(agent_name if is_agent else "User")
        bg_color = generate_color_from_string(agent_name if is_agent else "User")
        avatar_html = f'<div class="avatar" style="background-color: {bg_color};">{initials}</div>'

    message_body = format_message_content(message_data['Message'])

    return f"""
        <div class="{message_class}">
            <div class="message-content-wrapper">
                {avatar_html}
                <div class="message-content speech-bubble">
                    <div class="message-header">
                        <span class="sender">{agent_name if is_agent else 'User'}</span>
                        <span class="timestamp">{message_data['Timestamp'].strftime('%Y-%m-%d %H:%M')}</span>
                    </div>
                    <div class="message-text">{message_body}</div>
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
                .stApp [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > div:nth-child(2) {
                    overflow-y: auto;
                    max-height: 75vh;
                }

                .message-content-wrapper {
                    display: flex;
                    align-items: flex-start;
                    margin: 15px 0;
                }

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

                .speech-bubble {
                    position: relative;
                    max-width: 70%;
                    padding: 12px 15px;
                    border-radius: 10px;
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
                    text-align: left;
                    word-break: break-word;
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

                .message-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 5px;
                    text-align: left;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    padding-bottom: 5px;
                    font-size: 0.9em;
                }

                .sender {
                    font-weight: bold;
                }

                .timestamp {
                    font-size: 0.8em;
                    opacity: 0.7;
                }

                .message-text {
                    white-space: pre-wrap;
                    line-height: 1.5;
                    overflow-wrap: break-word;
                }

                .message-text pre {
                    background-color: rgba(255,255,255,0.05);
                    padding: 10px;
                    border-radius: 6px;
                    font-size: 0.85rem;
                    font-family: monospace;
                    overflow-x: auto;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        for _, row in messages_df.iterrows():
            st.markdown(
                render_message(
                    message_data=row,
                    is_agent=row['Agent'] in selected_agents if selected_agents else False
                ),
                unsafe_allow_html=True
            )
