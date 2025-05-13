from flask import render_template

from . import routes, AuthSession # import routes object and authsession from initialiser file

# append all front-end GET routes to routes object, with corresponding HTML template response, ensuring user is authenticated for necesarry pages

@routes.route('/', methods=['GET'])
@routes.route('/config', methods=['GET'])
@AuthSession.auth_required
def configPage():
   return render_template('config.html')

@routes.route('/authenticate', methods=['GET'])
def authPage():
   return render_template('authenticate.html')

@routes.route("/configcreate", methods=['GET'])
@AuthSession.auth_required
def configCreatePage():
   return render_template('configcreate.html')

@routes.route("/configremove", methods=['GET'])
@AuthSession.auth_required
def configRemovePage():
   return render_template('configremove.html')
  
