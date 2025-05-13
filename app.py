from flask import Flask

from config import DevelopmentConfig as CurrentConfig

app = Flask(__name__) # initialise flask app object
app.config.from_object(CurrentConfig) # load configuration data from imported configuration

with app.app_context(): # allow access to app configuration data throughout rest of program
    from routes import * # import from routes, beginning with initialiser file

app.register_blueprint(routes) # append all routes to flask blueprint 
app.run(debug=True)