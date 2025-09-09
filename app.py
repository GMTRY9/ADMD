from flask import Flask
from flask_socketio import SocketIO
from config import DevelopmentConfig as CurrentConfig
from hardware.manager import drinkmachine

def create_app():
    app = Flask(__name__)
    app.config.from_object(CurrentConfig)

    with app.app_context():
        from routes import routes, register_socketio  # import blueprint + socketio binder
    app.register_blueprint(routes)

    socketio.init_app(app)  # bind socketio
    drinkmachine.set_socketio(socketio)
    register_socketio(socketio)  # give socketio to routes

    return app

if __name__ == "__main__":
    try:
        socketio = SocketIO(cors_allowed_origins="*")  # create globally
        socketio.run(create_app(), debug=False, host="0.0.0.0", port=80)
        pass
    finally:
        drinkmachine.cleanup()
