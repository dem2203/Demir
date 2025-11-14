# Main AI Engine - Always runs 24/7
worker: python main.py --mode=production

# Optional Dashboard - Can be closed anytime
web: streamlit run streamlit_app.py --server.port=$PORT --logger.level=error

# Health Monitor - Keeps system alive
monitor: python -c "from health_monitor import HealthMonitor; import os; m = HealthMonitor(dict(os.environ)); m.start_monitoring(60)"
