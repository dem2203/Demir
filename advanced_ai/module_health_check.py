# utils/module_health_check.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MODULE HEALTH CHECK - SYSTEM DIAGNOSTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Real-time module loading status and health monitoring
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import logging
import sys
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# MODULE HEALTH CHECKER
# ============================================================================

class ModuleHealthChecker:
    """
    Track which modules are loaded and working
    
    Provides real-time diagnostics about system health
    """
    
    def __init__(self):
        self.modules = {}  # module_name: {status, error, loaded_at}
        self.startup_time = datetime.now()
    
    def check_module(self, module_name: str) -> Dict[str, Any]:
        """Check if module is loaded"""
        if module_name in sys.modules:
            return {
                'name': module_name,
                'status': 'LOADED ✅',
                'loaded': True,
                'error': None,
            }
        else:
            return {
                'name': module_name,
                'status': 'NOT LOADED ❌',
                'loaded': False,
                'error': 'Module not found in sys.modules'
            }
    
    def register_module(self, module_name: str, status: str, error: str = None):
        """Register module status"""
        self.modules[module_name] = {
            'name': module_name,
            'status': status,
            'error': error,
            'checked_at': datetime.now().isoformat()
        }
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        loaded_modules = [m for m in self.modules.values() if '✅' in m['status']]
        failed_modules = [m for m in self.modules.values() if '❌' in m['status']]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.startup_time).total_seconds(),
            'total_modules_checked': len(self.modules),
            'loaded_count': len(loaded_modules),
            'failed_count': len(failed_modules),
            'success_rate': (len(loaded_modules) / max(len(self.modules), 1) * 100),
            'loaded_modules': loaded_modules,
            'failed_modules': failed_modules,
        }
    
    def get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        report = self.get_health_report()
        loaded = report['loaded_modules']
        failed = report['failed_modules']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DEMIR AI - Module Health Dashboard</title>
            <style>
                body {{ font-family: Arial; background: #1e1e1e; color: #fff; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                h1 {{ color: #00ff00; }}
                .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .loaded {{ background: #0a3d0a; border-left: 4px solid #00ff00; }}
                .failed {{ background: #3d0a0a; border-left: 4px solid #ff0000; }}
                .module-list {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
                .metric {{ background: #2a2a2a; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .success {{ color: #00ff00; }}
                .error {{ color: #ff0000; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 DEMIR AI v7.0 - Module Health Dashboard</h1>
                
                <div class="metric">
                    <h2>📊 System Status</h2>
                    <p><strong>Timestamp:</strong> {report['timestamp']}</p>
                    <p><strong>Uptime:</strong> {report['uptime_seconds']:.1f}s</p>
                    <p><strong>Total Modules Checked:</strong> {report['total_modules_checked']}</p>
                    <p><span class="success">✅ Loaded: {report['loaded_count']}</span></p>
                    <p><span class="error">❌ Failed: {report['failed_count']}</span></p>
                    <p><strong>Success Rate:</strong> {report['success_rate']:.1f}%</p>
                </div>
                
                <h2>✅ Loaded Modules ({len(loaded)})</h2>
                <div class="module-list">
        """
        
        for mod in loaded:
            html += f"""
                    <div class="status loaded">
                        <strong>{mod['name']}</strong><br>
                        Status: {mod['status']}<br>
                        <small>{mod.get('checked_at', 'N/A')}</small>
                    </div>
            """
        
        html += """
                </div>
                
                <h2>❌ Failed Modules (
        """
        html += f"{len(failed)})</h2>"
        
        if failed:
            html += """
                <div class="module-list">
            """
            for mod in failed:
                html += f"""
                        <div class="status failed">
                            <strong>{mod['name']}</strong><br>
                            Status: {mod['status']}<br>
                            Error: {mod.get('error', 'Unknown')}<br>
                            <small>{mod.get('checked_at', 'N/A')}</small>
                        </div>
                """
            html += """
                </div>
            """
        else:
            html += "<p class='success'>No failed modules!</p>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html

# ============================================================================
# GLOBAL HEALTH CHECKER
# ============================================================================

health_checker = ModuleHealthChecker()
