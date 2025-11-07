"""
🔮 LAYER PERFORMANCE TRACKER v1.0
=================================

Date: 7 Kasım 2025, 14:52 CET
Phase: 8.2 - Historical Accuracy Tracking

AMAÇ:
-----
Geçmiş 100 analizin sonuçlarını cache'le ve
her layer'ın accuracy/confidence'ini track et.
"""

import json
from datetime import datetime, timedelta
import os

CACHE_FILE = "layer_performance_cache.json"

def init_cache():
    """Initialize empty cache structure"""
    return {
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        'analyses': [],  # List of last 100 analyses
        'layer_stats': {
            'strategy': {'hits': 0, 'total': 0, 'avg_score': 50},
            'kelly': {'hits': 0, 'total': 0, 'avg_score': 50},
            'macro': {'hits': 0, 'total': 0, 'avg_score': 50},
            'gold': {'hits': 0, 'total': 0, 'avg_score': 50},
            'cross_asset': {'hits': 0, 'total': 0, 'avg_score': 50},
            'vix': {'hits': 0, 'total': 0, 'avg_score': 50},
            'monte_carlo': {'hits': 0, 'total': 0, 'avg_score': 50},
            'news': {'hits': 0, 'total': 0, 'avg_score': 50},
            'trad_markets': {'hits': 0, 'total': 0, 'avg_score': 50},
            'black_scholes': {'hits': 0, 'total': 0, 'avg_score': 50},
            'kalman': {'hits': 0, 'total': 0, 'avg_score': 50},
            'fractal': {'hits': 0, 'total': 0, 'avg_score': 50},
            'fourier': {'hits': 0, 'total': 0, 'avg_score': 50},
            'copula': {'hits': 0, 'total': 0, 'avg_score': 50},
            'rates': {'hits': 0, 'total': 0, 'avg_score': 50},
        }
    }

def load_cache():
    """Load or create cache"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return init_cache()

def save_cache(cache):
    """Save cache to file"""
    try:
        cache['updated'] = datetime.now().isoformat()
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except:
        pass

def record_analysis(final_score, signal, layers_data, realized_direction=None):
    """
    Record an analysis result
    
    Args:
        final_score: AI final score (0-100)
        signal: 'LONG', 'SHORT', 'NEUTRAL'
        layers_data: dict of {layer_name: score}
        realized_direction: Actual market direction (if known) - 'UP', 'DOWN', 'NEUTRAL'
    """
    cache = load_cache()
    
    # Create record
    record = {
        'timestamp': datetime.now().isoformat(),
        'final_score': final_score,
        'signal': signal,
        'layers': layers_data,
        'realized': realized_direction,
        'correct': None
    }
    
    # If we know real direction, mark if correct
    if realized_direction:
        predicted_up = signal in ['LONG', 'BUY']
        actual_up = realized_direction == 'UP'
        record['correct'] = (predicted_up == actual_up)
    
    # Add to analyses (keep last 100)
    cache['analyses'].append(record)
    if len(cache['analyses']) > 100:
        cache['analyses'] = cache['analyses'][-100:]
    
    # Update layer stats
    for layer_name, score in layers_data.items():
        if layer_name in cache['layer_stats']:
            stats = cache['layer_stats'][layer_name]
            stats['total'] += 1
            stats['avg_score'] = (stats['avg_score'] * (stats['total']-1) + score) / stats['total']
            
            # If we know actual direction, count hits
            if realized_direction and record['correct'] is not None:
                layer_signal = 'LONG' if score >= 60 else ('SHORT' if score <= 40 else 'NEUTRAL')
                if (layer_signal == 'LONG' and actual_up) or \
                   (layer_signal == 'SHORT' and not actual_up) or \
                   (layer_signal == 'NEUTRAL' and realized_direction == 'NEUTRAL'):
                    stats['hits'] += 1
    
    save_cache(cache)
    return record

def get_layer_accuracy(layer_name):
    """Get accuracy for specific layer"""
    cache = load_cache()
    if layer_name not in cache['layer_stats']:
        return None
    
    stats = cache['layer_stats'][layer_name]
    if stats['total'] == 0:
        return None
    
    accuracy = stats['hits'] / stats['total']
    return {
        'accuracy': round(accuracy, 3),
        'hits': stats['hits'],
        'total': stats['total'],
        'avg_score': round(stats['avg_score'], 2),
        'confidence': min(stats['total'] / 50, 1.0)  # Max confidence at 50 samples
    }

def get_all_layer_accuracies():
    """Get all layer accuracies sorted"""
    cache = load_cache()
    results = {}
    
    for layer_name in cache['layer_stats']:
        acc = get_layer_accuracy(layer_name)
        if acc:
            results[layer_name] = acc
    
    # Sort by accuracy descending
    return dict(sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True))

def get_performance_weights():
    """
    Get layer weights based on historical performance
    
    Returns:
        dict: {layer_name: adaptive_weight}
    """
    accuracies = get_all_layer_accuracies()
    
    if not accuracies:
        # Default equal weights if no history
        return {layer: 0.067 for layer in range(15)}
    
    weights = {}
    base_weight = 1.0 / 15
    
    for layer_name, stats in accuracies.items():
        accuracy = stats['accuracy']
        confidence = stats['confidence']
        
        # Adaptive weight: higher accuracy + higher confidence = higher weight
        # But with dampening to avoid extreme weights
        adjustment = 0.8 + (accuracy - 0.5) * 0.4 + (confidence - 0.5) * 0.2
        weights[layer_name] = base_weight * adjustment
    
    # Normalize
    total = sum(weights.values())
    weights = {k: v/total for k, v in weights.items()}
    
    return weights


if __name__ == "__main__":
    print("🔮 LAYER PERFORMANCE TRACKER TEST")
    print("="*50)
    
    # Simulate recording an analysis
    test_layers = {
        'black_scholes': 65,
        'kalman': 58,
        'fractal': 52,
        'fourier': 47,
        'copula': 55,
    }
    
    record_analysis(
        final_score=55.6,
        signal='NEUTRAL',
        layers_data=test_layers,
        realized_direction='DOWN'
    )
    
    # Get accuracies
    accs = get_all_layer_accuracies()
    print(f"\nRecorded. Total analyses: {len(load_cache()['analyses'])}")
    
    if accs:
        print("\nLayer Accuracies:")
        for layer, stats in list(accs.items())[:5]:
            print(f"  {layer}: {stats['accuracy']:.1%} ({stats['total']} samples)")
