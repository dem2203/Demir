# Procfile - Fixed for Railway execution permissions
web: python -m streamlit.cli run streamlit_app.py --logger.level=error --client.showErrorDetails=false --server.port=$PORT
worker: python main.py
