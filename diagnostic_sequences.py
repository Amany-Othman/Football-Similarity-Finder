"""
Diagnostic Script - Check Player ID Matching Issue
===================================================
"""

import pandas as pd

# Load the data
raw_data_path = r'F:\Football-Similarity-Finder\data\Raw_Encoded_England_Team_Only_Possession_Features.csv'
normalized_data_path = r'F:\Football-Similarity-Finder\data\Normalized_Oredered_England_Team_Only.csv'

raw_df = pd.read_csv(raw_data_path)
normalized_df = pd.read_csv(normalized_data_path)

print("="*80)
print("DIAGNOSTIC: Checking Player ID Matching")
print("="*80)
print()

# Check raw data player IDs
print("RAW DATA SAMPLE (first 10 rows):")
print("-"*80)
print(raw_df[['gameid', 'passerplayerid', 'receiverplayerid']].head(10))
print()

print("RAW DATA Player ID Types:")
print(f"  passerplayerid type: {type(raw_df['passerplayerid'].iloc[0])}")
print(f"  receiverplayerid type: {type(raw_df['receiverplayerid'].iloc[0])}")
print(f"  Sample passerplayerid values: {raw_df['passerplayerid'].unique()[:10]}")
print()

# Check normalized data player IDs
print("NORMALIZED DATA SAMPLE (first 10 rows):")
print("-"*80)
print(normalized_df[['gameid', 'playerid', 'positiongrouptype']].head(10))
print()

print("NORMALIZED DATA Player ID Types:")
print(f"  playerid type: {type(normalized_df['playerid'].iloc[0])}")
print(f"  Sample playerid values: {normalized_df['playerid'].unique()[:10]}")
print()

# Check for matching
print("="*80)
print("MATCHING CHECK")
print("="*80)
print()

# Get unique player IDs from both datasets
raw_players = set(raw_df['passerplayerid'].astype(str).unique())
raw_players.update(raw_df['receiverplayerid'].astype(str).unique())

norm_players = set(normalized_df['playerid'].astype(str).unique())

print(f"Unique players in RAW data: {len(raw_players)}")
print(f"Unique players in NORMALIZED data: {len(norm_players)}")
print(f"Players in BOTH datasets: {len(raw_players & norm_players)}")
print(f"Players ONLY in RAW: {len(raw_players - norm_players)}")
print(f"Players ONLY in NORMALIZED: {len(norm_players - raw_players)}")
print()

# Show examples of non-matching IDs
if len(raw_players - norm_players) > 0:
    print("Sample RAW player IDs NOT in NORMALIZED:")
    print(list(raw_players - norm_players)[:10])
    print()

if len(norm_players - raw_players) > 0:
    print("Sample NORMALIZED player IDs NOT in RAW:")
    print(list(norm_players - raw_players)[:10])
    print()

# Check if there's a game_id filtering issue
print("="*80)
print("GAME ID CHECK")
print("="*80)
print()

raw_games = set(raw_df['gameid'].unique())
norm_games = set(normalized_df['gameid'].unique())

print(f"Games in RAW: {sorted(raw_games)}")
print(f"Games in NORMALIZED: {sorted(norm_games)}")
print(f"Games in BOTH: {sorted(raw_games & norm_games)}")
print()

# For each game, check player matching
print("="*80)
print("PER-GAME PLAYER MATCHING")
print("="*80)
print()

for game_id in sorted(raw_games):
    raw_game_players = set(raw_df[raw_df['gameid'] == game_id]['passerplayerid'].astype(str).unique())
    raw_game_players.update(raw_df[raw_df['gameid'] == game_id]['receiverplayerid'].astype(str).unique())
    
    norm_game_players = set(normalized_df[normalized_df['gameid'] == game_id]['playerid'].astype(str).unique())
    
    overlap = len(raw_game_players & norm_game_players)
    print(f"Game {game_id}:")
    print(f"  RAW players: {len(raw_game_players)}")
    print(f"  NORMALIZED players: {len(norm_game_players)}")
    print(f"  Matching: {overlap} ({overlap/len(raw_game_players)*100:.1f}%)")
    
    if overlap < len(raw_game_players):
        print(f"  Missing from NORMALIZED: {raw_game_players - norm_game_players}")
    print()

print("="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)