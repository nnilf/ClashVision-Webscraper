from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict
import re
from utils import clean_cell, clean_text

def get_building_stats(soup: BeautifulSoup) -> Dict[str, pd.DataFrame]:
    results = {}
    tables = soup.find_all('table', class_='wikitable')

    if not tables:
        return results

    # Find the first table that has both:
    # 1. A column containing "Level" (case insensitive)
    # 2. A column containing "Hitpoints" or "HP" (case insensitive)
    main_table = None
    for table in tables:
        headers = []
        for th in table.find_all('th'):
            header = clean_text(th.get_text())
            if header and header not in headers:
                headers.append(header)
        
        # Check for both Level and Hitpoints/HP columns
        has_level = any(re.search(r'level', header, re.IGNORECASE) for header in headers)
        has_hp = any(re.search(r'hitpoints|hp', header, re.IGNORECASE) for header in headers)
        
        if has_level and has_hp:
            main_table = table
            break

    if not main_table:
        return results

    main_stats = parse_wikitable(main_table)
    if main_stats.empty:
        return results

    results['Main Stats'] = main_stats
    expected_row_count = len(main_stats)

    variation_count = 1  # For generic naming: Variation 1, 2, etc.

    # Get the index of the main table to only process tables after it
    main_table_index = tables.index(main_table)
    
    for table in tables[main_table_index + 1:]:
        df = parse_wikitable(table)
        if df.empty or len(df) != expected_row_count:
            continue  # Skip tables that don't match the main row count

        # Name them as Variation 1, Variation 2, etc.
        key = f"Variation {variation_count}"
        results[key] = df
        variation_count += 1

    return results

def parse_wikitable(table) -> pd.DataFrame:
    """Parse wikitable with consistent cleaning"""
    headers = []
    for th in table.find_all('th'):
        header = clean_text(th.get_text())
        if header and header not in headers:
            headers.append(header)

    rows = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        if not cells:
            continue

        row_data = [clean_cell(' '.join(
            line.strip() for line in cell.get_text().split('\n') if line.strip()
        )) for cell in cells]

        if len(row_data) >= len(headers):
            rows.append(row_data[:len(headers)])

    if not headers or not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=headers)
    df.columns = [clean_text(col) for col in df.columns]

    # Find any column that contains "level" (case insensitive)
    level_col = None
    for col in df.columns:
        if re.search(r'level', col, re.IGNORECASE):
            level_col = col
            break

    if level_col:
        # Rename the level column to 'Level' for consistency
        if level_col != 'Level':
            df = df.rename(columns={level_col: 'Level'})
        # Move Level column to first position
        cols = ['Level'] + [col for col in df.columns if col != 'Level']
        return df[cols]
    
    return df