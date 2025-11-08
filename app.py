#!/usr/bin/env python3
import subprocess
import sys

if __name__ == '__main__':
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py', 
                   '--server.port=8000', 
                   '--server.enableCORS=false', 
                   '--server.enableXsrfProtection=false',
                   '--logger.level=error'], 
                  cwd='/app')
