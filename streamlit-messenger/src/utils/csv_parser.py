import pandas as pd
from datetime import datetime

def load_messages(file_path: str) -> pd.DataFrame:
    """
    Load messages from a CSV file and return a pandas DataFrame.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: DataFrame containing messages with columns:
            - Timestamp (datetime)
            - Agent (str)
            - Message (str)
    """
    try:
        df = pd.read_csv(file_path)
        
        # Ensure required columns exist
        required_columns = {'Timestamp', 'Agent', 'Message'}
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")
        
        # Convert timestamp strings to datetime objects
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('Timestamp')
        
        return df
        
    except Exception as e:
        raise Exception(f"Error loading messages: {str(e)}")

def filter_messages(df: pd.DataFrame, 
                   agents: list[str] = None,
                   start_date: datetime = None,
                   end_date: datetime = None,
                   search_query: str = None) -> pd.DataFrame:
    """
    Filter messages based on various criteria.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing messages
        agents (list[str], optional): List of agents to include
        start_date (datetime, optional): Start date for filtering
        end_date (datetime, optional): End date for filtering
        search_query (str, optional): Text to search for in messages
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    if agents:
        filtered_df = filtered_df[filtered_df['Agent'].isin(agents)]
        
    if start_date:
        filtered_df = filtered_df[filtered_df['Timestamp'] >= start_date]
        
    if end_date:
        filtered_df = filtered_df[filtered_df['Timestamp'] <= end_date]
        
    if search_query:
        filtered_df = filtered_df[
            filtered_df['Message'].str.contains(search_query, case=False, na=False)
        ]
    
    return filtered_df