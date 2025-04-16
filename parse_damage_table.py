from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict

def get_building_stats(building_name: str, soup: BeautifulSoup) -> Dict[str, pd.DataFrame]:
    results = {}
    tables = soup.find_all('table', class_='wikitable')

    if not tables:
        return results

    # Always include the first table as main stats
    main_stats = parse_wikitable(tables[0])
    if main_stats.empty:
        return results

    results['Main Stats'] = main_stats
    expected_row_count = len(main_stats)

    variation_count = 1  # For generic naming: Variation 1, 2, etc.

    for table in tables[1:]:
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

    if 'Level' in df.columns:
        cols = ['Level'] + [col for col in df.columns if col != 'Level']
        return df[cols]
    elif 'level' in (col.lower() for col in df.columns):
        level_col = next(col for col in df.columns if 'level' in col.lower())
        df = df.rename(columns={level_col: 'Level'})
        return df[['Level'] + [col for col in df.columns if col != 'Level']]
    return df

def clean_text(text: str) -> str:
    """Clean wiki text formatting"""
    return re.sub(r'\[.*?\]|Edit|\.|\u200e|\u202f', '', text).strip()

def clean_cell(text: str):
    """Clean and convert cell values"""
    text = clean_text(text)
    if text.replace(',', '').replace('.', '').isdigit():
        return float(text.replace(',', '')) if '.' in text else int(text.replace(',', ''))
    if text.endswith('%'):
        try:
            return float(text[:-1]) / 100
        except ValueError:
            pass
    if text.lower() in ('n/a', '?', '-', '', 'none'):
        return None
    return text
