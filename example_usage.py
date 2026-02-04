"""
Example Usage Script - FIXED VERSION (Windows Compatible)
==========================================================

Fixed issues:
1. Windows UTF-8 encoding properly configured
2. All Unicode arrows replaced with ASCII '->'
3. Pattern statistics now correctly displays positions
"""

import sys
import pandas as pd
from pass_similarity_algorithm import PassSimilarityAnalyzer

# Fix Windows console encoding issues
import io
import os

# Force UTF-8 output with proper error handling for Windows
if sys.platform == 'win32':
    # For Windows, reconfigure stdout
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python < 3.7
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def load_and_prepare_data():
    """Load data and rename columns to match algorithm expectations"""
    
    print("Loading data files...")
    
    # File paths - UPDATE THESE TO YOUR ACTUAL PATHS
    raw_data_path = r'F:\Football-Similarity-Finder\data\Raw_Encoded_England_Team_Only_Possession_Features.csv'
    normalized_data_path = r'F:\Football-Similarity-Finder\data\Normalized_Oredered_England_Team_Only.csv'
    filtered_data_path = r'F:\Football-Similarity-Finder\data\Ball_Normalized_Filtered_England_Team_Only.csv'
    
    # Load the data
    raw_df = pd.read_csv(raw_data_path)
    normalized_df = pd.read_csv(normalized_data_path)
    filtered_df = pd.read_csv(filtered_data_path)
    
    print(f"  - Raw data: {len(raw_df)} rows")
    print(f"  - Normalized data: {len(normalized_df)} rows")
    print(f"  - Filtered data: {len(filtered_df)} rows")
    print()
    
    # Rename columns in raw data
    raw_column_mapping = {
        'possessioneventid': 'possessione',
        'passerplayerid': 'playerpass',
        'receiverplayerid': 'receiveplay',
        'possessioneventtype': 'eventtype'
    }
    
    raw_rename = {old: new for old, new in raw_column_mapping.items() if old in raw_df.columns}
    if raw_rename:
        raw_df = raw_df.rename(columns=raw_rename)
        print(f"[OK] Renamed raw columns: {raw_rename}")
    
    # Rename columns in normalized data
    norm_column_mapping = {
        'possessioneventid': 'possessione',
        'possessioneventtype': 'eventtype'
    }
    
    norm_rename = {old: new for old, new in norm_column_mapping.items() if old in normalized_df.columns}
    if norm_rename:
        normalized_df = normalized_df.rename(columns=norm_rename)
        print(f"[OK] Renamed normalized columns: {norm_rename}")
    
    # Rename columns in filtered data
    filt_column_mapping = {
        'possessioneventid': 'possessione',
        'possessioneventtype': 'eventtype'
    }
    
    filt_rename = {old: new for old, new in filt_column_mapping.items() if old in filtered_df.columns}
    if filt_rename:
        filtered_df = filtered_df.rename(columns=filt_rename)
        print(f"[OK] Renamed filtered columns: {filt_rename}")
    
    print()
    
    # Verify required columns exist
    print("Verifying required columns...")
    
    raw_required = ['gameid', 'playerpass', 'receiveplay', 'starttime', 'endtime', 'duration', 'eventtype', 'possessione']
    raw_missing = [col for col in raw_required if col not in raw_df.columns]
    if raw_missing:
        print(f"  [ERROR] Raw data missing columns: {raw_missing}")
    else:
        print(f"  [OK] Raw data has all required columns")
    
    norm_required = ['gameid', 'playerid', 'positiongrouptype']
    norm_missing = [col for col in norm_required if col not in normalized_df.columns]
    if norm_missing:
        print(f"  [ERROR] Normalized data missing columns: {norm_missing}")
    else:
        print(f"  [OK] Normalized data has all required columns for position mapping")
    
    filt_required = ['gameid', 'ball_x', 'ball_y', 'starttime']
    filt_missing = [col for col in filt_required if col not in filtered_df.columns]
    if filt_missing:
        print(f"  [WARNING] Filtered data missing columns: {filt_missing}")
    else:
        print(f"  [OK] Filtered data has ball position columns")
    
    print()
    
    return raw_df, normalized_df, filtered_df


def filter_sequences_intelligently(sequences, max_sequences=500):
    """
    Intelligently filter sequences to reduce comparisons while maintaining diversity.
    """
    from collections import defaultdict
    import random
    
    print(f"\nFiltering {len(sequences)} sequences to reduce comparisons...")
    
    # Group by length
    by_length = defaultdict(list)
    for seq in sequences:
        by_length[len(seq)].append(seq)
    
    print(f"  Sequences by length:")
    for length in sorted(by_length.keys()):
        print(f"    {length} passes: {len(by_length[length])} sequences")
    
    # Sample from each length group, prioritizing longer sequences
    filtered = []
    total_weight = sum(length * len(seqs) for length, seqs in by_length.items())
    
    for length, seqs in sorted(by_length.items(), reverse=True):
        weight = length * len(seqs)
        target_count = int((weight / total_weight) * max_sequences)
        target_count = max(target_count, min(10, len(seqs)))
        
        if len(seqs) <= target_count:
            filtered.extend(seqs)
        else:
            sampled = random.sample(seqs, target_count)
            filtered.extend(sampled)
    
    print(f"\n  Filtered down to: {len(filtered)} sequences")
    print(f"  Comparisons reduced from {len(sequences)*(len(sequences)-1)//2:,} to {len(filtered)*(len(filtered)-1)//2:,}")
    print()
    
    return filtered


def main():
    """Main execution function"""
    
    print("=" * 80)
    print("FOOTBALL PASS SIMILARITY ANALYZER - WITH ACTUAL POSITIONS")
    print("=" * 80)
    print()
    
    # Step 1: Configure the analyzer
    print("Step 1: Configuring analyzer...")
    config = {
        # Sequence parameters
        'min_sequence_length': 4,
        'max_sequence_length': 8,
        'max_time_gap': 8.0,
        
        # Similarity thresholds
        'similarity_threshold': 0.65,
        
        # Weight configuration
        'position_weight': 0.30,
        'spatial_weight': 0.25,
        'temporal_weight': 0.15,
        'structural_weight': 0.15,
        'sequence_weight': 0.15,
        
        # Analysis options
        'same_game_comparison': True,
        'spatial_tolerance': 10.0,
        'ngram_size': 3,
        
        # Use detailed positions
        'use_detailed_positions': True
    }
    
    analyzer = PassSimilarityAnalyzer(config)
    print("[OK] Analyzer configured")
    print("  Using ACTUAL player positions from data (not approximations!)")
    print()
    
    # Step 2: Load and prepare data
    print("Step 2: Loading and preparing data...")
    try:
        raw_df, normalized_df, filtered_df = load_and_prepare_data()
    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Extract passing sequences
    print("Step 3: Extracting passing sequences with ACTUAL positions...")
    print("  Note: Using NORMALIZED data for positions, FILTERED data for ball coords")
    print()
    try:
        sequences = analyzer.extract_sequences(raw_df, normalized_df, filtered_df)
        print(f"\n[OK] Extracted {len(sequences)} sequences")
        
        if len(sequences) == 0:
            print("\n[WARNING] No sequences found!")
            return
        
        print()
    except Exception as e:
        print(f"[ERROR] Failed to extract sequences: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3.5: INTELLIGENT FILTERING
    print("Step 3.5: Applying intelligent filtering...")
    max_sequences = 500
    
    if len(sequences) > max_sequences:
        sequences = filter_sequences_intelligently(sequences, max_sequences)
    else:
        print(f"  Sequences ({len(sequences)}) already below threshold, no filtering needed")
        print()
    
    # Step 4: Find similar patterns
    print("Step 4: Finding similar passing patterns...")
    total_comparisons = len(sequences) * (len(sequences) - 1) // 2
    print(f"  Will perform {total_comparisons:,} comparisons")
    print()
    
    try:
        results = analyzer.find_similar_patterns(sequences, top_k=20)
        print(f"[OK] Found {len(results)} similar patterns")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to find similar patterns: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 5: Generate and display report (with safe encoding)
    if results:
        print("Step 5: Generating analysis report...")
        try:
            report = analyzer.generate_report(results)
            # Already uses ASCII arrows in the algorithm
            print(report)
        except Exception as e:
            print(f"[ERROR] Failed to generate report: {e}")
            import traceback
            traceback.print_exc()
        
        # Step 6: Export results
        print("Step 6: Exporting results...")
        try:
            analyzer.export_results(results, 'similarity_results_with_positions.json')
            print("[OK] Results exported to: similarity_results_with_positions.json")
            print()
        except Exception as e:
            print(f"[ERROR] Failed to export results: {e}")
            import traceback
            traceback.print_exc()
        
        # Step 7: Additional analysis
        print("=" * 80)
        print("ADDITIONAL INSIGHTS")
        print("=" * 80)
        print()
        
        # Calculate statistics
        scores = [r.overall_score for r in results]
        seq_sims = [r.sequence_similarity for r in results]
        spatial_sims = [r.spatial_similarity for r in results]
        
        print(f"Average Overall Similarity: {sum(scores)/len(scores):.2%}")
        print(f"Average Sequence Similarity: {sum(seq_sims)/len(seq_sims):.2%}")
        print(f"Average Spatial Similarity: {sum(spatial_sims)/len(spatial_sims):.2%}")
        print()
        
        # Sequence length distribution
        seq_lengths = {}
        for result in results:
            length = len(result.seq1)
            seq_lengths[length] = seq_lengths.get(length, 0) + 1
        
        print("Similar patterns by sequence length:")
        for length in sorted(seq_lengths.keys()):
            print(f"  {length} passes: {seq_lengths[length]} patterns")
        print()
        
        # Most common patterns WITH ACTUAL POSITIONS (safe encoding - already ASCII)
        from collections import Counter
        all_patterns = []
        for result in results:
            # Already using ASCII arrow from generate_report
            pattern_parts = []
            for e in result.seq1.pattern:
                pattern_parts.append(f"{e['from']}->{e['to']}")
            pattern = ' -> '.join(pattern_parts)
            all_patterns.append(pattern)
        
        print("Most Common Pattern Types (with actual positions!):")
        for pattern, count in Counter(all_patterns).most_common(10):
            print(f"  {count}x: {pattern}")
        print()
        
        # Analyze specific position usage
        print("\nPosition Transition Analysis:")
        position_pairs = Counter()
        for result in results:
            for event in result.seq1.pattern:
                position_pairs[(event['from'], event['to'])] += 1
        
        print("Most common position-to-position passes in similar patterns:")
        for (pos_from, pos_to), count in position_pairs.most_common(15):
            print(f"  {pos_from} -> {pos_to}: {count} occurrences")
        print()
        
        # Show some example patterns in detail
        print("\nExample Similar Patterns (Top 5):")
        print("=" * 80)
        for i, result in enumerate(results[:5], 1):
            print(f"\nPattern #{i} (Similarity: {result.overall_score:.1%})")
            print(f"  Game {result.seq1.game_id} vs Game {result.seq2.game_id}")
            print(f"  Length: {len(result.seq1)} passes")
            
            # Pattern 1
            pattern1_parts = []
            for event in result.seq1.events:
                pattern1_parts.append(f"{event.position_from}")
            pattern1_parts.append(result.seq1.events[-1].position_to)
            pattern1_str = " -> ".join(pattern1_parts)
            print(f"  Sequence 1: {pattern1_str}")
            
            # Pattern 2
            pattern2_parts = []
            for event in result.seq2.events:
                pattern2_parts.append(f"{event.position_from}")
            pattern2_parts.append(result.seq2.events[-1].position_to)
            pattern2_str = " -> ".join(pattern2_parts)
            print(f"  Sequence 2: {pattern2_str}")
            
            print(f"  Details:")
            print(f"    - Sequence Similarity: {result.sequence_similarity:.1%}")
            print(f"    - Spatial Similarity:  {result.spatial_similarity:.1%}")
            print(f"    - Temporal Similarity: {result.temporal_similarity:.1%}")
        
        print("\n" + "=" * 80)
        
    else:
        print("\n[INFO] No similar patterns found.")
        print("Try adjusting these parameters:")
        print("  - Lower similarity_threshold (currently 0.65)")
        print("  - Increase max_time_gap (currently 8.0 seconds)")
        print("  - Reduce min_sequence_length (currently 4)")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Total sequences analyzed: {len(sequences)}")
    print(f"  - Similar patterns found: {len(results)}")
    print(f"  - Results saved to: similarity_results_with_positions.json")
    print()


if __name__ == "__main__":
    main()