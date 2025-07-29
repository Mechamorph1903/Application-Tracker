from app import create_app
import os

app = create_app()

if __name__ == '__main__':
	# Only use Flask's built-in server for local development
	port = int(os.environ.get('PORT', 5000))
	debug = os.environ.get('FLASK_ENV') == 'development'
	app.run(host='0.0.0.0', port=port, debug=debug)  # Run the app

