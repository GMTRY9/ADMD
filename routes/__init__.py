from flask import Blueprint, current_app
from .authmanager import AuthManager

# currentUserConfig = ["", ""] # initialise global variable
# # currentUserConfig = ["(ConfigName)", "(Current Config's HTML)"]

AuthSession = AuthManager(current_app.config["SECRET_KEY"]) # initialise constant authmanager object with environment secret

routes = Blueprint('routes', __name__)

# append all routes from api.py and index.py
from .api import * 
from .index import *