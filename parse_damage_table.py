from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict

# Mapping of all defensive buildings and their attack modes
BUILDING_MODES = {
    'archer_tower': ['Fast Attack', 'Long Attack'],
    'cannon': ['Burst Mode'],
    'mortar': ['Splash Attack'],
    'inferno_tower': ['Single Target', 'Multi Target'],
    'x-bow': ['Ground Mode', 'Air Mode'],
    'eagle_artillery': ['Activated', 'Inactive'],
    'scattershot': ['Normal Attack', 'Spread Attack'],
    'builder_hut': ['Normal Attack', 'Battle Pop'],
    'multi-mortar': ['Standard Mode', 'Burst Mode'],
    'bomb_tower': ['Normal Attack', 'Air Bombs'],
    'tesla': ['Normal Attack', 'Rapid Fire']
}


def get_building_stats(building_name: str, soup: BeautifulSoup) -> Dict[str, pd.DataFrame]:
    """
    Get complete statistics for any defensive building including all attack modes.
    Handles both standard (/Home_Village) and special URL structures.
    
    Args:
        building_name: Building name as it appears in URL (e.g., 'Mortar', 'Archer_Tower')
        soup: Soup element containing entire HTML page
        
    Returns:
        Dictionary with keys: 
        - 'Main Stats' (always present)
        - Other mode-specific keys when applicable
    """
    
    building_key = building_name.lower()
    
    # Special case handlers
    if building_key == 'mortar':
        return handle_mortar(soup)
    elif building_key == 'bomb_tower':
        return handle_bomb_tower(soup)
    
    return handle_standard_building(soup, building_key)


def handle_mortar(soup: BeautifulSoup) -> Dict[str, pd.DataFrame]:
    """Special handler for Mortar's unique page structure"""
    results = {}
    
    # Main stats table - Mortar has it in the first wikitable
    main_table = soup.find('table', {'class': 'wikitable'})
    if main_table:
        df = parse_wikitable(main_table)
        if not df.empty:
            results['Main Stats'] = df
    
    # Splash damage table - found after the Splash Damage heading
    for h2 in soup.find_all('h2'):
        if 'splash damage' in h2.get_text().lower():
            splash_table = h2.find_next('table', class_='wikitable')
            if splash_table:
                df = parse_wikitable(splash_table)
                if not df.empty:
                    results['Splash Attack'] = df
            break
    
    return results


def handle_bomb_tower(soup: BeautifulSoup) -> Dict[str, pd.DataFrame]:
    """Special handler for Bomb Tower's air bombs"""
    results = {}
    
    # Main stats table
    main_table = soup.find('table', {'class': 'wikitable'})
    if main_table:
        df = parse_wikitable(main_table)
        if not df.empty:
            results['Main Stats'] = df
    
    # Air bombs table
    for h3 in soup.find_all('h3'):
        if 'air bombs' in h3.get_text().lower():
            air_table = h3.find_next('table')
            if air_table:
                df = parse_wikitable(air_table)
                if not df.empty:
                    results['Air Bombs'] = df
            break
    
    return results


def handle_standard_building(soup: BeautifulSoup, building_key: str) -> Dict[str, pd.DataFrame]:
    """Handler for most buildings with standard layout"""
    results = {}
    tables = soup.find_all('table', class_='wikitable')
    expected_modes = BUILDING_MODES.get(building_key, [])
    
    for table in tables:
        if len(table.find_all('tr')) < 3:  # Skip small tables
            continue
            
        table_name = identify_table(table, building_key)
        df = parse_wikitable(table)
        
        if not df.empty:
            if table_name == 'Main Stats':
                if 'Main Stats' not in results:
                    results['Main Stats'] = df
            elif table_name in expected_modes:
                results[table_name] = df
    
    return results


def identify_table(table, building_key: str) -> str:
    """Identify table type based on context and building type"""
    prev_elements = table.find_previous(['h2', 'h3', 'h4', 'p', 'b'])
    prev_text = prev_elements.get_text().lower() if prev_elements else ""
    
    # Check for known modes for this building
    for mode in BUILDING_MODES.get(building_key, []):
        if mode.lower() in prev_text:
            return mode
    
    # Special text pattern matching
    if 'burst' in prev_text and building_key == 'cannon':
        return 'Burst Mode'
    if 'splash' in prev_text and building_key == 'mortar':
        return 'Splash Attack'
    if 'air bomb' in prev_text and building_key == 'bomb_tower':
        return 'Air Bombs'
    
    return 'Main Stats'


def parse_wikitable(table) -> pd.DataFrame:
    """Robust wikitable parser with comprehensive cleaning"""
    headers = []
    for th in table.find_all('th'):
        header = clean_text(th.get_text())
        if header and header not in headers:
            headers.append(header)
    
    rows = []
    for row in table.find_all('tr')[1:]:  # Skip header row
        cells = row.find_all('td')
        if not cells:
            continue
            
        row_data = []
        for cell in cells:
            cell_text = ' '.join(line.strip() for line in cell.get_text().split('\n') if line.strip())
            cleaned = clean_cell(cell_text)
            row_data.append(cleaned)
        
        if len(row_data) == len(headers):
            rows.append(row_data)
        elif len(row_data) > len(headers):
            rows.append(row_data[:len(headers)])
    
    if not headers or not rows:
        return pd.DataFrame()
    
    df = pd.DataFrame(rows, columns=headers)
    
    # Standardize columns
    df.columns = [clean_text(col) for col in df.columns]
    
    # Make Level first column if exists
    level_cols = [col for col in df.columns if 'level' in col.lower()]
    if level_cols:
        df = df.rename(columns={level_cols[0]: 'Level'})
        cols = ['Level'] + [col for col in df.columns if col != 'Level']
        df = df[cols]
    
    return df


def clean_text(text: str) -> str:
    """Clean text by removing wiki formatting and special characters"""
    text = re.sub(r'\[.*?\]|Edit|\.|\u200e|\u202f', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def clean_cell(text: str):
    """Clean and convert cell values to appropriate types"""
    text = clean_text(text)
    
    if text.replace(',', '').replace('.', '').isdigit():
        text = text.replace(',', '')
        return float(text) if '.' in text else int(text)
    
    if text.endswith('%'):
        try:
            return float(text[:-1]) / 100
        except ValueError:
            pass
    
    if text.lower() in ('n/a', '?', '-', '', 'none'):
        return None
    
    return text