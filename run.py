"""
This is the main entry point to run the Flask application.
"""
from api.server import app

if __name__ == '__main__':
    # Running in debug mode is convenient for development.
    # For production, use a proper WSGI server like Gunicorn or uWSGI.
    app.run(debug=True, port=5000)