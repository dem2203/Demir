web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
api: gunicorn --workers 1 --threads 4 --worker-class gthread --bind 0.0.0.0:$PORT api_server:app
bot: python main.py
stream: python market_stream.py
