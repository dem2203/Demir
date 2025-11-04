# feedback_system.py - User Feedback Collection System
"""
🎯 DEMIR AI TRADING BOT - User Feedback System
====================================================================
Date: 4 Kasım 2025, 11:55 CET
Version: 1.0 - Initial Release

PURPOSE:
--------
Kullanıcılardan AI sinyalleri, layer performansı ve sistem deneyimi
hakkında geri bildirim toplar.

FEATURES:
---------
✅ Signal accuracy feedback (Was signal correct?)
✅ Layer-specific feedback (Which layers performed well?)
✅ UX feedback (UI/UX improvement suggestions)
✅ Bug reporting
✅ Performance tracking
✅ Anonymous analytics
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

class FeedbackSystem:
    """User feedback collection and analytics"""
    
    def __init__(self, db_path='feedback.db'):
        """Initialize feedback system"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create feedback database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Signal accuracy feedback
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS signal_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            ai_signal TEXT NOT NULL,
            ai_score REAL NOT NULL,
            ai_confidence REAL NOT NULL,
            user_feedback TEXT NOT NULL,
            actual_outcome TEXT,
            profit_loss REAL,
            notes TEXT,
            user_id TEXT
        )
        ''')
        
        # Layer performance feedback
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS layer_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            layer_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            accuracy_perception INTEGER,
            usefulness INTEGER,
            comments TEXT,
            user_id TEXT
        )
        ''')
        
        # UX feedback
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ux_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            category TEXT NOT NULL,
            rating INTEGER NOT NULL,
            suggestion TEXT,
            bug_description TEXT,
            severity TEXT,
            user_id TEXT
        )
        ''')
        
        # Performance metrics
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            page_name TEXT NOT NULL,
            load_time_ms INTEGER,
            api_response_time_ms INTEGER,
            error_occurred INTEGER,
            error_message TEXT,
            user_id TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Feedback database initialized")
    
    # ========================================================================
    # SIGNAL FEEDBACK
    # ========================================================================
    
    def submit_signal_feedback(self, 
                              symbol: str,
                              timeframe: str,
                              ai_signal: str,
                              ai_score: float,
                              ai_confidence: float,
                              user_feedback: str,
                              actual_outcome: Optional[str] = None,
                              profit_loss: Optional[float] = None,
                              notes: Optional[str] = None,
                              user_id: str = 'anonymous') -> int:
        """
        Submit feedback about an AI signal
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            timeframe: Interval (e.g., 1h, 4h)
            ai_signal: AI's signal (LONG, SHORT, NEUTRAL)
            ai_score: AI confidence score (0-100)
            ai_confidence: AI confidence percentage
            user_feedback: User's assessment (CORRECT, INCORRECT, PARTIAL, TOO_EARLY)
            actual_outcome: Actual market movement
            profit_loss: P/L if trade was taken
            notes: Additional comments
            user_id: User identifier
        
        Returns:
            Feedback ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO signal_feedback (
            timestamp, symbol, timeframe, ai_signal, ai_score, ai_confidence,
            user_feedback, actual_outcome, profit_loss, notes, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            symbol,
            timeframe,
            ai_signal,
            ai_score,
            ai_confidence,
            user_feedback,
            actual_outcome,
            profit_loss,
            notes,
            user_id
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Signal feedback submitted: ID {feedback_id}")
        return feedback_id
    
    def get_signal_accuracy_stats(self, days: int = 30) -> Dict:
        """
        Calculate AI signal accuracy from user feedback
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Accuracy statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get feedback from last N days
        cursor.execute('''
        SELECT user_feedback, COUNT(*) as count
        FROM signal_feedback
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        GROUP BY user_feedback
        ''', (days,))
        
        results = cursor.fetchall()
        conn.close()
        
        total = sum(count for _, count in results)
        
        if total == 0:
            return {
                'total_feedbacks': 0,
                'accuracy_rate': 0.0,
                'correct': 0,
                'incorrect': 0,
                'partial': 0,
                'too_early': 0
            }
        
        feedback_counts = dict(results)
        correct = feedback_counts.get('CORRECT', 0)
        incorrect = feedback_counts.get('INCORRECT', 0)
        partial = feedback_counts.get('PARTIAL', 0) * 0.5  # Partial = 50% credit
        
        accuracy = ((correct + partial) / total) * 100
        
        return {
            'total_feedbacks': total,
            'accuracy_rate': round(accuracy, 2),
            'correct': feedback_counts.get('CORRECT', 0),
            'incorrect': feedback_counts.get('INCORRECT', 0),
            'partial': feedback_counts.get('PARTIAL', 0),
            'too_early': feedback_counts.get('TOO_EARLY', 0),
            'period_days': days
        }
    
    # ========================================================================
    # LAYER FEEDBACK
    # ========================================================================
    
    def submit_layer_feedback(self,
                             layer_name: str,
                             rating: int,
                             accuracy_perception: Optional[int] = None,
                             usefulness: Optional[int] = None,
                             comments: Optional[str] = None,
                             user_id: str = 'anonymous') -> int:
        """
        Submit feedback about a specific layer's performance
        
        Args:
            layer_name: Layer name (e.g., 'strategy', 'macro')
            rating: Overall rating (1-5)
            accuracy_perception: How accurate user thinks it is (1-5)
            usefulness: How useful user finds it (1-5)
            comments: Additional feedback
            user_id: User identifier
        
        Returns:
            Feedback ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO layer_feedback (
            timestamp, layer_name, rating, accuracy_perception, 
            usefulness, comments, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            layer_name,
            rating,
            accuracy_perception,
            usefulness,
            comments,
            user_id
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Layer feedback submitted: {layer_name} - ID {feedback_id}")
        return feedback_id
    
    def get_layer_ratings(self) -> Dict[str, Dict]:
        """Get average ratings for all layers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            layer_name,
            AVG(rating) as avg_rating,
            AVG(accuracy_perception) as avg_accuracy,
            AVG(usefulness) as avg_usefulness,
            COUNT(*) as feedback_count
        FROM layer_feedback
        GROUP BY layer_name
        ORDER BY avg_rating DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            row[0]: {
                'avg_rating': round(row[1], 2),
                'avg_accuracy': round(row[2], 2) if row[2] else None,
                'avg_usefulness': round(row[3], 2) if row[3] else None,
                'feedback_count': row[4]
            }
            for row in results
        }
    
    # ========================================================================
    # UX FEEDBACK
    # ========================================================================
    
    def submit_ux_feedback(self,
                          category: str,
                          rating: int,
                          suggestion: Optional[str] = None,
                          bug_description: Optional[str] = None,
                          severity: str = 'LOW',
                          user_id: str = 'anonymous') -> int:
        """
        Submit UX feedback or bug report
        
        Args:
            category: Feedback category (UI, Performance, Feature, Bug)
            rating: Overall satisfaction (1-5)
            suggestion: Improvement suggestion
            bug_description: Bug details
            severity: Bug severity (LOW, MEDIUM, HIGH, CRITICAL)
            user_id: User identifier
        
        Returns:
            Feedback ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO ux_feedback (
            timestamp, category, rating, suggestion, 
            bug_description, severity, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            category,
            rating,
            suggestion,
            bug_description,
            severity,
            user_id
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ UX feedback submitted: {category} - ID {feedback_id}")
        return feedback_id
    
    # ========================================================================
    # PERFORMANCE TRACKING
    # ========================================================================
    
    def track_performance(self,
                         page_name: str,
                         load_time_ms: int,
                         api_response_time_ms: Optional[int] = None,
                         error_occurred: bool = False,
                         error_message: Optional[str] = None,
                         user_id: str = 'anonymous'):
        """Track page/API performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO performance_metrics (
            timestamp, page_name, load_time_ms, api_response_time_ms,
            error_occurred, error_message, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            page_name,
            load_time_ms,
            api_response_time_ms,
            1 if error_occurred else 0,
            error_message,
            user_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_stats(self, page_name: Optional[str] = None) -> Dict:
        """Get performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if page_name:
            cursor.execute('''
            SELECT 
                AVG(load_time_ms) as avg_load,
                MAX(load_time_ms) as max_load,
                MIN(load_time_ms) as min_load,
                AVG(api_response_time_ms) as avg_api,
                SUM(error_occurred) as total_errors,
                COUNT(*) as total_requests
            FROM performance_metrics
            WHERE page_name = ?
            ''', (page_name,))
        else:
            cursor.execute('''
            SELECT 
                AVG(load_time_ms) as avg_load,
                MAX(load_time_ms) as max_load,
                MIN(load_time_ms) as min_load,
                AVG(api_response_time_ms) as avg_api,
                SUM(error_occurred) as total_errors,
                COUNT(*) as total_requests
            FROM performance_metrics
            ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'avg_load_time_ms': round(result[0], 2) if result[0] else 0,
            'max_load_time_ms': result[1] or 0,
            'min_load_time_ms': result[2] or 0,
            'avg_api_time_ms': round(result[3], 2) if result[3] else None,
            'total_errors': result[4] or 0,
            'total_requests': result[5] or 0,
            'error_rate': round((result[4] / result[5]) * 100, 2) if result[5] else 0
        }

# ============================================================================
# ANALYTICS & REPORTING
# ============================================================================

def generate_feedback_report(feedback_system: FeedbackSystem, days: int = 30) -> str:
    """Generate comprehensive feedback report"""
    report = []
    report.append("=" * 80)
    report.append("📊 USER FEEDBACK REPORT")
    report.append("=" * 80)
    report.append(f"Period: Last {days} days")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Signal accuracy
    signal_stats = feedback_system.get_signal_accuracy_stats(days)
    report.append("🎯 AI SIGNAL ACCURACY")
    report.append("-" * 80)
    report.append(f"Total Feedbacks: {signal_stats['total_feedbacks']}")
    report.append(f"Accuracy Rate: {signal_stats['accuracy_rate']}%")
    report.append(f"  ✅ Correct: {signal_stats['correct']}")
    report.append(f"  ❌ Incorrect: {signal_stats['incorrect']}")
    report.append(f"  ⚠️  Partial: {signal_stats['partial']}")
    report.append(f"  ⏰ Too Early: {signal_stats['too_early']}")
    report.append("")
    
    # Layer ratings
    layer_ratings = feedback_system.get_layer_ratings()
    report.append("📈 LAYER PERFORMANCE RATINGS")
    report.append("-" * 80)
    for layer, stats in sorted(layer_ratings.items(), 
                               key=lambda x: x[1]['avg_rating'], 
                               reverse=True):
        report.append(f"{layer:20s} | Rating: {stats['avg_rating']}/5 | "
                     f"Feedbacks: {stats['feedback_count']}")
    report.append("")
    
    # Performance metrics
    perf_stats = feedback_system.get_performance_stats()
    report.append("⚡ SYSTEM PERFORMANCE")
    report.append("-" * 80)
    report.append(f"Avg Load Time: {perf_stats['avg_load_time_ms']}ms")
    report.append(f"Max Load Time: {perf_stats['max_load_time_ms']}ms")
    report.append(f"Total Errors: {perf_stats['total_errors']}")
    report.append(f"Error Rate: {perf_stats['error_rate']}%")
    report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)


if __name__ == "__main__":
    # Test feedback system
    print("=" * 80)
    print("🧪 FEEDBACK SYSTEM TEST")
    print("=" * 80)
    
    fs = FeedbackSystem('test_feedback.db')
    
    # Test signal feedback
    fs.submit_signal_feedback(
        symbol='BTCUSDT',
        timeframe='1h',
        ai_signal='LONG',
        ai_score=72.5,
        ai_confidence=85.0,
        user_feedback='CORRECT',
        profit_loss=2.5,
        notes='Signal was accurate, entry timing perfect'
    )
    
    # Test layer feedback
    fs.submit_layer_feedback(
        layer_name='strategy',
        rating=5,
        accuracy_perception=4,
        usefulness=5,
        comments='Very helpful, consistent results'
    )
    
    # Test UX feedback
    fs.submit_ux_feedback(
        category='UI',
        rating=4,
        suggestion='Add dark mode toggle button'
    )
    
    # Generate report
    print("\n")
    print(generate_feedback_report(fs, days=30))
    
    print("\n✅ Feedback system test completed!")
