from app import create_app

app = create_app()

if __name__ == '__main__':
	app.run(debug=True)  # Run the app in debug mode for development

