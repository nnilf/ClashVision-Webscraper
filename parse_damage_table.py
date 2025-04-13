from bs4 import BeautifulSoup
import pandas as pd
import re

def parse_damage_table(table: BeautifulSoup) -> pd.DataFrame:
    """
    Parses a Clash of Clans building stats table from the wiki and returns a DataFrame.
    Handles different building types (defenses, resources, etc.) with varying stats.
    
    Args:
        table: BeautifulSoup object containing the HTML table to parse
        
    Returns:
        pd.DataFrame: DataFrame containing all available stats for each building level
    """
    # Find all rows, skip header rows which don't contain level data
    rows = table.find_all("tr")
    data_rows = [row for row in rows if row.find("td") and row.find("td").text.strip().isdigit()]
    
    if not data_rows:
        return pd.DataFrame()
    
    # Extract column headers from th elements
    headers = []
    header_row = rows[0]
    for th in header_row.find_all(["th", "td"]):
        header_text = th.text.strip()
        # Clean up header text
        header_text = re.sub(r'\[.*?\]', '', header_text)  # Remove any [notes]
        header_text = header_text.replace('\n', ' ').replace('\t', '')
        header_text = ' '.join(header_text.split())  # Collapse multiple spaces
        if header_text:
            headers.append(header_text)
    
    # For each data row, extract the values
    data = []
    for row in data_rows:
        cols = row.find_all("td")
        row_data = []
        
        for i, col in enumerate(cols):
            text = col.text.strip()
            text = re.sub(r'\[.*?\]', '', text)  # Remove any [notes]
            text = text.replace('\n', ' ').replace('\t', '')
            text = ' '.join(text.split())  # Collapse multiple spaces
            
            # Try to convert to number if possible
            if text.replace(',', '').replace('.', '').isdigit():
                text = text.replace(',', '')
                try:
                    if '.' in text:
                        text = float(text)
                    else:
                        text = int(text)
                except ValueError:
                    pass
            elif text.endswith('%'):
                try:
                    text = float(text[:-1]) / 100
                except ValueError:
                    pass
            
            row_data.append(text)
        
        # Pad row with None if it has fewer columns than headers
        if len(row_data) < len(headers):
            row_data += [None] * (len(headers) - len(row_data))
        
        data.append(row_data)
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=headers[:len(data[0])])
    
    # Clean up column names
    df.columns = df.columns.str.strip()
    
    # Ensure 'Level' column is first if it exists
    if 'Level' in df.columns and df.columns[0] != 'Level':
        cols = df.columns.tolist()
        cols.insert(0, cols.pop(cols.index('Level')))
        df = df[cols]
    
    return df