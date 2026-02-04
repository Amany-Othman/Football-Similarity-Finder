"""
Modified Pass Similarity Analyzer for single-pass-per-possession data structure
================================================================================

This version reconstructs passing sequences by linking consecutive passes
where receiver becomes the next passer.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class PassEvent:
    """Represents a single pass event in a sequence."""
    game_id: int
    possession_id: int
    player_from: str
    player_to: str
    position_from: str
    position_to: str
    start_time: float
    end_time: float
    duration: float
    event_type: str
    ball_x: Optional[float] = None
    ball_y: Optional[float] = None


@dataclass
class PassSequence:
    """Represents a sequence of connected passes."""
    game_id: int
    possession_id: int
    events: List[PassEvent]
    pattern: List[Dict]
    start_time: float
    end_time: float
    duration: float
    
    def __len__(self):
        return len(self.events)


@dataclass
class SimilarityResult:
    """Result of similarity comparison between two sequences."""
    seq1: PassSequence
    seq2: PassSequence
    overall_score: float
    sequence_similarity: float
    spatial_similarity: float
    temporal_similarity: float
    structural_similarity: float
    
    def to_dict(self):
        return {
            'game1': self.seq1.game_id,
            'game2': self.seq2.game_id,
            'overall_score': self.overall_score,
            'sequence_similarity': self.sequence_similarity,
            'spatial_similarity': self.spatial_similarity,
            'temporal_similarity': self.temporal_similarity,
            'structural_similarity': self.structural_similarity,
            'pattern1': [f"{e['from']}->{e['to']}" for e in self.seq1.pattern],
            'pattern2': [f"{e['from']}->{e['to']}" for e in self.seq2.pattern]
        }


class PassSimilarityAnalyzer:
    """
    Modified analyzer for data where each possession is a single pass event.
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'min_sequence_length': 3,
            'max_sequence_length': 15,
            'similarity_threshold': 0.70,
            'position_weight': 0.3,
            'spatial_weight': 0.25,
            'temporal_weight': 0.15,
            'structural_weight': 0.15,
            'sequence_weight': 0.15,
            'same_game_comparison': False,
            'max_time_gap': 5.0,
            'spatial_tolerance': 10.0,
            'ngram_size': 3
        }
        self.config = {**default_config, **(config or {})}
        
        self.position_hierarchy = {
            'GK': 1,
            'DF': 2,
            'MF': 3,
            'FW': 4
        }
    
    def load_data(self, raw_data_path: str, normalized_data_path: str, 
                  filtered_data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load and validate all required data files."""
        raw_df = pd.read_csv(raw_data_path)
        normalized_df = pd.read_csv(normalized_data_path)
        filtered_df = pd.read_csv(filtered_data_path)
        
        print(f"Loaded data:")
        print(f"  - Raw data: {len(raw_df)} rows")
        print(f"  - Normalized data: {len(normalized_df)} rows")
        print(f"  - Filtered data: {len(filtered_df)} rows")
        
        return raw_df, normalized_df, filtered_df
    
    def map_player_to_position(self, player_id: str, player_mapping: Dict = None) -> str:
        """Map player ID to position category."""
        if player_mapping and player_id in player_mapping:
            return player_mapping[player_id]
        
        try:
            pid = int(float(player_id))  # Handle float player IDs
            if pid == 1 or pid == 10:
                return 'GK'
            elif pid <= 500:
                return 'DF'
            elif pid <= 2000:
                return 'MF'
            else:
                return 'FW'
        except (ValueError, TypeError):
            return 'UNKNOWN'
    
    def extract_sequences(self, raw_df: pd.DataFrame, 
                         ball_df: pd.DataFrame = None) -> List[PassSequence]:
        """
        Extract passing sequences by linking consecutive passes.
        In this data structure, each row is a single pass, so we need to
        link passes where the receiver becomes the next passer.
        """
        sequences = []
        min_len = self.config['min_sequence_length']
        max_len = self.config['max_sequence_length']
        max_gap = self.config['max_time_gap']
        
        print(f"\nExtracting sequences with:")
        print(f"  - Min length: {min_len} passes")
        print(f"  - Max length: {max_len} passes")
        print(f"  - Max time gap: {max_gap} seconds")
        print()
        
        # Group by game
        for game_id, game_group in raw_df.groupby('gameid'):
            # Sort by time
            game_group = game_group.sort_values('starttime').reset_index(drop=True)
            
            print(f"Processing Game {game_id}: {len(game_group)} passes")
            
            # Build sequences by chaining passes
            current_seq = []
            
            for idx, row in game_group.iterrows():
                # Create pass event
                event = PassEvent(
                    game_id=game_id,
                    possession_id=row['possessione'],
                    player_from=str(row['playerpass']),
                    player_to=str(row['receiveplay']),
                    position_from=self.map_player_to_position(row['playerpass']),
                    position_to=self.map_player_to_position(row['receiveplay']),
                    start_time=row['starttime'],
                    end_time=row['endtime'],
                    duration=row['duration'],
                    event_type=row['eventtype']
                )
                
                # Add ball position if available
                if ball_df is not None:
                    ball_row = ball_df[
                        (ball_df['gameid'] == game_id) & 
                        (abs(ball_df['starttime'] - row['starttime']) < 0.1)
                    ]
                    if not ball_row.empty:
                        event.ball_x = ball_row.iloc[0].get('ball_x')
                        event.ball_y = ball_row.iloc[0].get('ball_y')
                
                # Check if this pass continues the sequence
                can_continue = False
                if current_seq:
                    last_event = current_seq[-1]
                    time_gap = event.start_time - last_event.end_time
                    
                    # Pass continues if:
                    # 1. Receiver of last pass = passer of current pass
                    # 2. Time gap is within threshold
                    if (last_event.player_to == event.player_from and 
                        time_gap <= max_gap and time_gap >= 0):
                        can_continue = True
                
                if can_continue:
                    current_seq.append(event)
                else:
                    # Save current sequence if it meets criteria
                    if len(current_seq) >= min_len:
                        sequences.extend(self._create_subsequences(current_seq, min_len, max_len))
                    # Start new sequence
                    current_seq = [event]
            
            # Don't forget the last sequence
            if len(current_seq) >= min_len:
                sequences.extend(self._create_subsequences(current_seq, min_len, max_len))
            
            print(f"  Found {len([s for s in sequences if s.game_id == game_id])} sequences")
        
        print(f"\nTotal extracted: {len(sequences)} sequences")
        return sequences
    
    def _create_subsequences(self, events: List[PassEvent], 
                            min_len: int, max_len: int) -> List[PassSequence]:
        """Create overlapping subsequences from a list of events."""
        subsequences = []
        
        for length in range(min_len, min(len(events) + 1, max_len + 1)):
            for i in range(len(events) - length + 1):
                sub_events = events[i:i + length]
                
                pattern = [
                    {
                        'from': e.position_from,
                        'to': e.position_to,
                        'duration': e.duration,
                        'event_type': e.event_type
                    }
                    for e in sub_events
                ]
                
                seq = PassSequence(
                    game_id=sub_events[0].game_id,
                    possession_id=sub_events[0].possession_id,
                    events=sub_events,
                    pattern=pattern,
                    start_time=sub_events[0].start_time,
                    end_time=sub_events[-1].end_time,
                    duration=sub_events[-1].end_time - sub_events[0].start_time
                )
                
                subsequences.append(seq)
        
        return subsequences
    
    def levenshtein_distance(self, pattern1: List[Dict], pattern2: List[Dict]) -> float:
        """Calculate Levenshtein distance between two patterns with custom costs."""
        m, n = len(pattern1), len(pattern2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = self._pattern_cost(pattern1[i-1], pattern2[j-1])
                dp[i][j] = min(
                    dp[i-1][j] + 1,
                    dp[i][j-1] + 1,
                    dp[i-1][j-1] + cost
                )
        
        return dp[m][n]
    
    def _pattern_cost(self, p1: Dict, p2: Dict) -> float:
        """Calculate substitution cost between two pattern elements."""
        cost = 0.0
        
        if p1['from'] != p2['from']:
            cost += 0.5
        if p1['to'] != p2['to']:
            cost += 0.5
        
        duration_diff = abs(p1['duration'] - p2['duration']) / max(p1['duration'], p2['duration'], 1)
        cost += duration_diff * 0.3
        
        if p1.get('event_type') != p2.get('event_type'):
            cost += 0.2
        
        return min(cost, 1.0)
    
    def calculate_spatial_similarity(self, seq1: PassSequence, seq2: PassSequence) -> float:
        """Calculate spatial similarity using ball position data."""
        coords1 = [(e.ball_x, e.ball_y) for e in seq1.events if e.ball_x is not None]
        coords2 = [(e.ball_x, e.ball_y) for e in seq2.events if e.ball_y is not None]
        
        if not coords1 or not coords2:
            return 0.0
        
        dtw_dist = self._dtw_distance(coords1, coords2)
        max_dist = np.sqrt(100**2 + 100**2)
        normalized_dist = dtw_dist / (len(coords1) * max_dist)
        
        return max(0, 1 - normalized_dist)
    
    def _dtw_distance(self, series1: List[Tuple], series2: List[Tuple]) -> float:
        """Dynamic Time Warping distance between two spatial series."""
        n, m = len(series1), len(series2)
        dtw = np.full((n + 1, m + 1), np.inf)
        dtw[0, 0] = 0
        
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = np.sqrt(
                    (series1[i-1][0] - series2[j-1][0])**2 + 
                    (series1[i-1][1] - series2[j-1][1])**2
                )
                dtw[i, j] = cost + min(dtw[i-1, j], dtw[i, j-1], dtw[i-1, j-1])
        
        return dtw[n, m]
    
    def calculate_temporal_similarity(self, seq1: PassSequence, seq2: PassSequence) -> float:
        """Calculate temporal similarity based on pass timing and rhythm."""
        intervals1 = [seq1.events[i].start_time - seq1.events[i-1].end_time 
                     for i in range(1, len(seq1.events))]
        intervals2 = [seq2.events[i].start_time - seq2.events[i-1].end_time 
                     for i in range(1, len(seq2.events))]
        
        if not intervals1 or not intervals2:
            return 0.0
        
        mean_diff = abs(np.mean(intervals1) - np.mean(intervals2))
        std_diff = abs(np.std(intervals1) - np.std(intervals2))
        
        temporal_sim = 1 / (1 + mean_diff + std_diff)
        
        return temporal_sim
    
    def calculate_structural_similarity(self, seq1: PassSequence, seq2: PassSequence) -> float:
        """Calculate structural similarity based on position transitions."""
        trans1 = self._build_transition_matrix(seq1)
        trans2 = self._build_transition_matrix(seq2)
        
        similarity = 0.0
        count = 0
        
        for pos_from in self.position_hierarchy.keys():
            for pos_to in self.position_hierarchy.keys():
                if (pos_from, pos_to) in trans1 or (pos_from, pos_to) in trans2:
                    val1 = trans1.get((pos_from, pos_to), 0)
                    val2 = trans2.get((pos_from, pos_to), 0)
                    similarity += 1 - abs(val1 - val2)
                    count += 1
        
        return similarity / count if count > 0 else 0.0
    
    def _build_transition_matrix(self, seq: PassSequence) -> Dict[Tuple[str, str], float]:
        """Build position transition frequency matrix."""
        transitions = defaultdict(int)
        total = 0
        
        for event in seq.events:
            transitions[(event.position_from, event.position_to)] += 1
            total += 1
        
        return {k: v / total for k, v in transitions.items()}
    
    def calculate_similarity(self, seq1: PassSequence, seq2: PassSequence) -> SimilarityResult:
        """Calculate overall similarity between two sequences using weighted metrics."""
        max_len = max(len(seq1), len(seq2))
        lev_dist = self.levenshtein_distance(seq1.pattern, seq2.pattern)
        seq_sim = 1 - (lev_dist / max_len)
        
        spatial_sim = self.calculate_spatial_similarity(seq1, seq2)
        temporal_sim = self.calculate_temporal_similarity(seq1, seq2)
        structural_sim = self.calculate_structural_similarity(seq1, seq2)
        
        overall = (
            seq_sim * self.config['sequence_weight'] +
            spatial_sim * self.config['spatial_weight'] +
            temporal_sim * self.config['temporal_weight'] +
            structural_sim * self.config['structural_weight'] +
            seq_sim * self.config['position_weight']
        )
        
        return SimilarityResult(
            seq1=seq1,
            seq2=seq2,
            overall_score=overall,
            sequence_similarity=seq_sim,
            spatial_similarity=spatial_sim,
            temporal_similarity=temporal_sim,
            structural_similarity=structural_sim
        )
    
    def find_similar_patterns(self, sequences: List[PassSequence], 
                             top_k: int = 10) -> List[SimilarityResult]:
        """Find the most similar passing patterns across all sequences."""
        results = []
        threshold = self.config['similarity_threshold']
        same_game_ok = self.config['same_game_comparison']
        
        total_comparisons = len(sequences) * (len(sequences) - 1) // 2
        print(f"\nComparing {len(sequences)} sequences ({total_comparisons} comparisons)...")
        
        comparison_count = 0
        for i in range(len(sequences)):
            for j in range(i + 1, len(sequences)):
                if not same_game_ok and sequences[i].game_id == sequences[j].game_id:
                    continue
                
                similarity = self.calculate_similarity(sequences[i], sequences[j])
                
                if similarity.overall_score >= threshold:
                    results.append(similarity)
                
                comparison_count += 1
                if comparison_count % 10000 == 0:
                    print(f"  Progress: {comparison_count}/{total_comparisons} comparisons")
        
        results.sort(key=lambda x: x.overall_score, reverse=True)
        
        print(f"\nFound {len(results)} similar patterns above threshold {threshold}")
        return results[:top_k]
    
    def export_results(self, results: List[SimilarityResult], 
                      output_path: str = 'similarity_results.json'):
        """Export results to JSON file."""
        export_data = {
            'config': self.config,
            'num_results': len(results),
            'results': [r.to_dict() for r in results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\nResults exported to {output_path}")
    
    def generate_report(self, results: List[SimilarityResult]) -> str:
        """Generate a human-readable analysis report."""
        if not results:
            return "No similar patterns found."
        
        report = []
        report.append("=" * 80)
        report.append("PASS SIMILARITY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nTotal Patterns Found: {len(results)}")
        report.append(f"Similarity Threshold: {self.config['similarity_threshold']:.2%}")
        report.append(f"\nTop 10 Most Similar Patterns:\n")
        
        for i, result in enumerate(results[:10], 1):
            report.append(f"\n{'-' * 80}")
            report.append(f"Rank #{i} - Overall Similarity: {result.overall_score:.2%}")
            report.append(f"{'-' * 80}")
            report.append(f"Match: Game {result.seq1.game_id} vs Game {result.seq2.game_id}")
            report.append(f"Sequence Length: {len(result.seq1)} passes")
            report.append(f"\nDetailed Scores:")
            report.append(f"  * Sequence Similarity: {result.sequence_similarity:.2%}")
            report.append(f"  * Spatial Similarity: {result.spatial_similarity:.2%}")
            report.append(f"  * Temporal Similarity: {result.temporal_similarity:.2%}")
            report.append(f"  * Structural Similarity: {result.structural_similarity:.2%}")
            
            pattern1_str = ' -> '.join([f"{e['from']}->{e['to']}" for e in result.seq1.pattern])
            pattern2_str = ' -> '.join([f"{e['from']}->{e['to']}" for e in result.seq2.pattern])
            
            report.append(f"\nPattern 1: {pattern1_str}")
            report.append(f"Pattern 2: {pattern2_str}")
        
        report.append(f"\n{'=' * 80}\n")
        return '\n'.join(report)