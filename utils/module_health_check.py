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
    """Track which modules are loaded and working"""
    
    def __init__(self):
        self.modules = {}
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
            <title>DEMIR AI - Module Health</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff00; padding: 20px; }}
                .container {{ max-width: 1400px; margin: 0 auto; }}
                h1 {{ color: #00ff00; font-size: 28px; margin-bottom: 20px; text-shadow: 0 0 10px #00ff00; }}
                h2 {{ color: #ffaa00; font-size: 20px; margin: 20px 0 10px 0; }}
                .metric {{ background: #1a1a1a; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #333; }}
                .metric p {{ margin: 8px 0; font-size: 14px; }}
                .success {{ color: #00ff00; }}
                .error {{ color: #ff3333; }}
                .module-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 10px; margin-top: 15px; }}
                .module-card {{ background: #1a1a1a; padding: 12px; border-radius: 6px; border-left: 4px solid #00ff00; font-size: 13px; }}
                .module-card.failed {{ border-left-color: #ff3333; }}
                .module-card strong {{ display: block; margin-bottom: 5px; color: #ffaa00; }}
                .module-card small {{ color: #666; font-size: 11px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 DEMIR AI v7.0 - Module Health Monitor</h1>
                
                <div class="metric">
                    <h2>📊 System Status</h2>
                    <p><strong>Timestamp:</strong> {report['timestamp']}</p>
                    <p><strong>Uptime:</strong> {report['uptime_seconds']:.1f}s</p>
                    <p><strong>Total Modules:</strong> {report['total_modules_checked']}</p>
                    <p class="success"><strong>✅ Loaded:</strong> {report['loaded_count']}</p>
                    <p class="error"><strong>❌ Failed:</strong> {report['failed_count']}</p>
                    <p><strong>Success Rate:</strong> {report['success_rate']:.1f}%</p>
                </div>
                
                <h2>✅ Loaded Modules ({len(loaded)})</h2>
                <div class="module-grid">
        """
        
        for mod in loaded:
            html += f"""
                    <div class="module-card">
                        <strong>{mod['name']}</strong>
                        Status: {mod['status']}<br>
                        <small>{mod.get('checked_at', 'N/A')}</small>
                    </div>
            """
        
        html += f"""
                </div>
                
                <h2>❌ Failed Modules ({len(failed)})</h2>
        """
        
        if failed:
            html += '<div class="module-grid">'
            for mod in failed:
                error_msg = mod.get('error', 'Unknown error')[:100]
                html += f"""
                        <div class="module-card failed">
                            <strong>{mod['name']}</strong>
                            Status: {mod['status']}<br>
                            Error: {error_msg}<br>
                            <small>{mod.get('checked_at', 'N/A')}</small>
                        </div>
                """
            html += '</div>'
        else:
            html += '<p class="success">✅ No failed modules! System is healthy.</p>'
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html

# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

health_checker = ModuleHealthChecker()
