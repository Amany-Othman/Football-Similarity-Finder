"""
Example Usage Script - OPTIMIZED VERSION
=========================================

This version uses smart filtering to reduce comparisons from millions to thousands.
"""

import sys
import pandas as pd
from pass_similarity_algorithm import PassSimilarityAnalyzer

def load_and_prepare_data():
    """Load data and rename columns to match algorithm expectations"""
    
    print("Loading data files...")
    
    # File paths
    raw_data_path = r'D:\Projects\dsp\Football-Similarity\data\Raw_Encoded_England_Team_Only_Possession_Features.csv'
    normalized_data_path = r'D:\Projects\dsp\Football-Similarity\data\Normalized_Oredered_England_Team_Only.csv'
    filtered_data_path = r'D:\Projects\dsp\Football-Similarity\data\Ball_Normalized_Filtered_England_Team_Only.csv'
    
    # Load the data
    raw_df = pd.read_csv(raw_data_path)
    normalized_df = pd.read_csv(normalized_data_path)
    filtered_df = pd.read_csv(filtered_data_path)
    
    print(f"  - Raw data: {len(raw_df)} rows")
    print(f"  - Normalized data: {len(normalized_df)} rows")
    print(f"  - Filtered data: {len(filtered_df)} rows")
    print()
    
    # Rename columns
    raw_column_mapping = {
        'possessioneventid': 'possessione',
        'passerplayerid': 'playerpass',
        'receiverplayerid': 'receiveplay',
        'possessioneventtype': 'eventtype'
    }
    
    raw_rename = {old: new for old, new in raw_column_mapping.items() if old in raw_df.columns}
    raw_df = raw_df.rename(columns=raw_rename)
    
    norm_column_mapping = {
        'possessioneventid': 'possessione',
        'possessioneventtype': 'eventtype'
    }
    
    norm_rename = {old: new for old, new in norm_column_mapping.items() if old in normalized_df.columns}
    normalized_df = normalized_df.rename(columns=norm_rename)
    
    filt_column_mapping = {
        'possessioneventid': 'possessione',
        'possessioneventtype': 'eventtype'
    }
    
    filt_rename = {old: new for old, new in filt_column_mapping.items() if old in filtered_df.columns}
    filtered_df = filtered_df.rename(columns=filt_rename)
    
    print("[OK] Column mapping complete")
    print()
    
    return raw_df, normalized_df, filtered_df


def filter_sequences_intelligently(sequences, max_sequences=500):
    """
    Intelligently filter sequences to reduce comparisons while maintaining diversity.
    
    Strategy:
    1. Group by length and pattern signature
    2. Sample from each group to maintain diversity
    3. Prioritize longer sequences (more interesting patterns)
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
    
    for length, seqs in sorted(by_length.items(), reverse=True):  # Longest first
        # Calculate how many to sample from this group
        weight = length * len(seqs)
        target_count = int((weight / total_weight) * max_sequences)
        target_count = max(target_count, min(10, len(seqs)))  # At least 10 per group
        
        if len(seqs) <= target_count:
            filtered.extend(seqs)
        else:
            # Randomly sample
            sampled = random.sample(seqs, target_count)
            filtered.extend(sampled)
    
    print(f"\n  Filtered down to: {len(filtered)} sequences")
    print(f"  Comparisons reduced from {len(sequences)*(len(sequences)-1)//2:,} to {len(filtered)*(len(filtered)-1)//2:,}")
    print()
    
    return filtered


def main():
    """Main execution function"""
    
    print("=" * 80)
    print("FOOTBALL PASS SIMILARITY ANALYZER - OPTIMIZED VERSION")
    print("=" * 80)
    print()
    
    # Step 1: Configure the analyzer
    print("Step 1: Configuring analyzer...")
    config = {
        # Sequence parameters
        'min_sequence_length': 4,      # Increase to 4 for more meaningful patterns
        'max_sequence_length': 8,      # Keep at 8
        'max_time_gap': 8.0,           # Reduce to 8 seconds for tighter sequences
        
        # Similarity thresholds
        'similarity_threshold': 0.65,   # 65% minimum similarity
        
        # Weight configuration
        'position_weight': 0.30,
        'spatial_weight': 0.25,
        'temporal_weight': 0.15,
        'structural_weight': 0.15,
        'sequence_weight': 0.15,
        
        # Analysis options
        'same_game_comparison': True,
        'spatial_tolerance': 10.0,
        'ngram_size': 3
    }
    
    analyzer = PassSimilarityAnalyzer(config)
    print("[OK] Analyzer configured")
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
    print("Step 3: Extracting passing sequences...")
    print()
    try:
        sequences = analyzer.extract_sequences(raw_df, filtered_df)
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
    max_sequences = 500  # Limit to 500 sequences max
    
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
        # Find top 20 most similar patterns
        results = analyzer.find_similar_patterns(sequences, top_k=20)
        print(f"[OK] Found {len(results)} similar patterns")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to find similar patterns: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 5: Generate and display report
    if results:
        print("Step 5: Generating analysis report...")
        try:
            report = analyzer.generate_report(results)
            print(report)
        except Exception as e:
            print(f"[ERROR] Failed to generate report: {e}")
            import traceback
            traceback.print_exc()
        
        # Step 6: Export results
        print("Step 6: Exporting results...")
        try:
            analyzer.export_results(results, 'similarity_results.json')
            print("[OK] Results exported to: similarity_results.json")
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
        
        # Find most common patterns
        from collections import Counter
        all_patterns = []
        for result in results:
            pattern = ' -> '.join([f"{e['from']}->{e['to']}" for e in result.seq1.pattern])
            all_patterns.append(pattern)
        
        print("Most Common Pattern Types:")
        for pattern, count in Counter(all_patterns).most_common(5):
            print(f"  {count}x: {pattern}")
        print()
    else:
        print("\n[INFO] No similar patterns found.")
        print("Try adjusting these parameters:")
        print("  - Lower similarity_threshold (currently 0.65)")
        print("  - Increase max_time_gap (currently 8.0 seconds)")
        print("  - Reduce min_sequence_length (currently 4)")
    
    print("=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print()
    print("Performance Summary:")
    print(f"  - Total sequences extracted: {len(sequences)}")
    print(f"  - Total comparisons: {total_comparisons:,}")
    print(f"  - Similar patterns found: {len(results)}")
    print()


if __name__ == "__main__":
    main()