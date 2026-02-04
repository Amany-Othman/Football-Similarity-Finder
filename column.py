"""
Script to inspect column names in your data files
"""
import pandas as pd

print("=" * 80)
print("DATA INSPECTION - Column Names")
print("=" * 80)
print()

# File paths
raw_data_path = r'D:\Projects\dsp\Football-Similarity\data\Raw_Encoded_England_Team_Only_Possession_Features.csv'
normalized_data_path = r'D:\Projects\dsp\Football-Similarity\data\Normalized_Oredered_England_Team_Only.csv'
filtered_data_path = r'D:\Projects\dsp\Football-Similarity\data\Ball_Normalized_Filtered_England_Team_Only.csv'

# Load and inspect raw data
print("1. RAW DATA FILE")
print("-" * 80)
try:
    raw_df = pd.read_csv(raw_data_path)
    print(f"Rows: {len(raw_df)}")
    print(f"Columns: {len(raw_df.columns)}")
    print()
    print("Column names:")
    for i, col in enumerate(raw_df.columns, 1):
        print(f"  {i:2d}. {col}")
    print()
    print("First few rows:")
    print(raw_df.head(3))
except Exception as e:
    print(f"Error loading raw data: {e}")

print()
print("=" * 80)
print()

# Load and inspect normalized data
print("2. NORMALIZED DATA FILE")
print("-" * 80)
try:
    norm_df = pd.read_csv(normalized_data_path)
    print(f"Rows: {len(norm_df)}")
    print(f"Columns: {len(norm_df.columns)}")
    print()
    print("Column names:")
    for i, col in enumerate(norm_df.columns, 1):
        print(f"  {i:2d}. {col}")
    print()
    print("First few rows:")
    print(norm_df.head(3))
except Exception as e:
    print(f"Error loading normalized data: {e}")

print()
print("=" * 80)
print()

# Load and inspect filtered data
print("3. FILTERED DATA FILE")
print("-" * 80)
try:
    filt_df = pd.read_csv(filtered_data_path)
    print(f"Rows: {len(filt_df)}")
    print(f"Columns: {len(filt_df.columns)}")
    print()
    print("Column names:")
    for i, col in enumerate(filt_df.columns, 1):
        print(f"  {i:2d}. {col}")
    print()
    print("First few rows:")
    print(filt_df.head(3))
except Exception as e:
    print(f"Error loading filtered data: {e}")

print()
print("=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)