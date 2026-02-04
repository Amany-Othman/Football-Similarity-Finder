"""
Diagnostic script to understand the sequence extraction issue
"""
import pandas as pd

# Load and prepare data
print("=" * 80)
print("DIAGNOSTIC - Why are no sequences being extracted?")
print("=" * 80)
print()

# File paths
raw_data_path = r'D:\Projects\dsp\Football-Similarity\data\Raw_Encoded_England_Team_Only_Possession_Features.csv'
normalized_data_path = r'D:\Projects\dsp\Football-Similarity\data\Normalized_Oredered_England_Team_Only.csv'

# Load the data
raw_df = pd.read_csv(raw_data_path)
normalized_df = pd.read_csv(normalized_data_path)

# Rename columns
raw_df = raw_df.rename(columns={
    'possessioneventid': 'possessione',
    'passerplayerid': 'playerpass',
    'receiverplayerid': 'receiveplay',
    'possessioneventtype': 'eventtype'
})

normalized_df = normalized_df.rename(columns={
    'possessioneventid': 'possessione',
    'possessioneventtype': 'eventtype'
})

print("1. CHECKING RAW DATA STRUCTURE")
print("-" * 80)
print(f"Total rows: {len(raw_df)}")
print(f"Columns: {list(raw_df.columns)}")
print()

# Check for PASS events
print("Event types in data:")
if 'eventtype' in raw_df.columns:
    event_counts = raw_df['eventtype'].value_counts()
    print(event_counts)
else:
    print("ERROR: 'eventtype' column not found!")
print()

# Check possession grouping
print("2. CHECKING POSSESSION GROUPING")
print("-" * 80)
grouped = raw_df.groupby(['gameid', 'possessione'])
print(f"Number of unique possessions: {len(grouped)}")
print()

# Sample a few possessions
print("Sample possession details (first 5 possessions):")
for i, ((game, poss), group) in enumerate(grouped):
    if i >= 5:
        break
    print(f"\nPossession {i+1}: Game={game}, Possession={poss}")
    print(f"  Events: {len(group)}")
    if 'eventtype' in group.columns:
        print(f"  Event types: {group['eventtype'].tolist()}")
    if 'playerpass' in group.columns and 'receiveplay' in group.columns:
        print(f"  Passers: {group['playerpass'].tolist()}")
        print(f"  Receivers: {group['receiveplay'].tolist()}")
    print(f"  Times: {group['starttime'].tolist()}")

print()
print("3. CHECKING FOR PASS SEQUENCES")
print("-" * 80)

# Manually check for sequences
sequence_count = 0
pass_count = 0

for (game, poss), group in grouped:
    # Filter for PASS events
    passes = group[group['eventtype'] == 'PASS'] if 'eventtype' in group.columns else group
    pass_count += len(passes)
    
    if len(passes) >= 3:  # Minimum sequence length
        sequence_count += 1

print(f"Total PASS events across all possessions: {pass_count}")
print(f"Possessions with 3+ passes: {sequence_count}")
print()

# Check what event type values actually exist
print("4. DETAILED EVENT TYPE ANALYSIS")
print("-" * 80)
print("Unique event type values:")
if 'eventtype' in raw_df.columns:
    unique_events = raw_df['eventtype'].unique()
    for evt in unique_events:
        count = len(raw_df[raw_df['eventtype'] == evt])
        print(f"  '{evt}': {count} events")
else:
    print("No 'eventtype' column found")
print()

# Check a sample possession in detail
print("5. SAMPLE POSSESSION IN DETAIL")
print("-" * 80)
first_poss = list(grouped.groups.keys())[0]
sample = grouped.get_group(first_poss)
print(f"Game ID: {first_poss[0]}, Possession ID: {first_poss[1]}")
print()
print(sample[['starttime', 'endtime', 'eventtype', 'playerpass', 'receiveplay']].to_string())
print()

print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)