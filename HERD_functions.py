import pandas as pd
import openpyxl


def find_best_header(df_preview):
    """
    Analyzes a preview DataFrame to find the row index with the most non-null values.
    This is likely the header row.
    """
    # Calculate the number of non-null values for each of the first 20 rows
    non_null_counts = df_preview.notna().sum(axis=1)
    
    # The best header is the one with the maximum non-null values
    best_header_index = non_null_counts.idxmax()
    
    return best_header_index

def get_key_from_value(d, val):
    """
    Returns the first key in dictionary 'd' that has the value 'val'.
    Raises ValueError if the value is not found.
    """
    for key, value in d.items():
        if value == val:
            return key
    raise ValueError(f"Value '{val}' not found in the dictionary.")
