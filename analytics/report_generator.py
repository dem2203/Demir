# report_generator.py - Automated Report Generation

import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate performance reports"""
    
    def __init__(self):
        self.reports = []
    
    def generate_daily_report(self, metrics, trades):
        """Generate daily report"""
        report = {
            'date': datetime.now().date(),
            'metrics': metrics,
            'trades': trades,
            'generated_at': datetime.now()
        }
        
        self.reports.append(report)
        logger.info(f"✅ Daily report generated")
        
        return report
    
    def export_to_json(self, filename):
        """Export report to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.reports, f, indent=2, default=str)
