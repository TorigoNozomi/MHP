# Streamlit Messenger

A Streamlit application for displaying conversation logs in a messenger-like interface.

## Features

- Upload and view CSV files containing conversation logs
- Filter messages by:
  - Agent (sender)
  - Date range
  - Search text
- Modern messenger-like UI with:
  - Chat bubbles
  - Avatars with unique colors for each agent
  - Timestamps
  - Markdown support in messages
- Reverse chronological order option
- Responsive design

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
cd src
streamlit run app.py
```

2. Upload a CSV file containing conversation logs
   - The CSV must have these columns:
     - `Timestamp`: Message timestamp (e.g., "2023-10-01 10:00:00")
     - `Agent`: Sender name
     - `Message`: Message content (supports Markdown)

3. Use the sidebar filters to:
   - Select specific agents
   - Choose a date range
   - Search for text in messages
   - Toggle message order

## CSV File Format Example

```csv
Timestamp,Agent,Message
2023-10-01 10:00:00,Alice,Hello!
2023-10-01 10:01:00,Bob,Hi Alice!
2023-10-01 10:02:00,Alice,How are you?
```

## Project Structure

```
streamlit-messenger/
├── README.md
├── requirements.txt
├── streamlit_config.toml
└── src/
    ├── app.py
    ├── components/
    │   ├── __init__.py
    │   ├── message.py
    │   └── message_list.py
    ├── styles/
    │   └── styles.css
    └── utils/
        ├── __init__.py
        └── csv_parser.py
```

## Customization

- Edit `src/styles/styles.css` to customize the appearance
- Modify `streamlit_config.toml` to change Streamlit settings
