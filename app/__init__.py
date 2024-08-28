from flask import Flask

def create_app():
    app = Flask(__name__)

    # Add your app configuration here

    # Add your app routes here

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()