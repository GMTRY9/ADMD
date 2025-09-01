from flask import Blueprint, current_app
from .authmanager import AuthManager
from hardware import DrinkMachine

routes = Blueprint("routes", __name__)
AuthSession = AuthManager(current_app.config["SECRET_KEY"])
# drinkmachine = DrinkMachine()

def register_socketio(socketio):
    @socketio.on("connect")
    def handle_connect():
        print("Client connected")

# import routes AFTER blueprint/socketio setup
from .api import *
from .index import *
