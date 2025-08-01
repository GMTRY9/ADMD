import json
from flask import request, jsonify

from hardware import *
from .authmanager import AuthManager

from . import AuthSession, routes # import constants from initialiser file

drinkmachine = DrinkMachine()

@routes.route('/api/authenticate', methods=['GET'])
def authDevice():
   if request.method == 'GET':
      response = AuthSession.authenticate(request.args.get('authcode'), request.remote_addr) # pass OTP authcode into authenticate method
      return response

@routes.route('/api/editconfig', methods=['POST'])
@AuthSession.auth_required
def editConfig():
   if request.method == 'POST': 
      new_config = request.get_json()
      if not new_config['name']:
         return jsonify(error="Field values should be populated"), 400
      
      old_config = UserConfigurationLoader(drinkmachine.get_selected_config_name()).load() # load current user config to be edited

      # edit config's button's keybinds to new entered keybinds
      system_cartridges = SystemConfigurationLoader().load().get_cartridges()

      for cartridge in range(1, system_cartridges+1):     
         proportion = new_config["proportions"][str(cartridge)]

         if not proportion:
            continue

         value = float(proportion)

         if value <= 0:
            return jsonify(error="Volume must be greater than 0"), 400
         
         old_config.set_proportion(str(cartridge), value)

      name = new_config['name']

      # ensure inputs are digits
      if len(name) < 1:
         return jsonify(error="Must enter a drink name"), 400
      elif name in UserConfigurationManager.list_configs() and name != old_config.get_name():
         return jsonify(error="Config name already exists"), 400
      
      old_config.set_name(name)

      # overwrite edited config
      UserConfigurationSaver(old_config).save(new_config["configNo"])

      return jsonify(success=True), 201

@routes.route("/api/configcreate", methods=['POST'])
@AuthSession.auth_required
def configCreate():
   if request.method == "POST":
      newconfig = request.get_json()

      # get configname and gridsizes from form data
      configname = newconfig["name"]

      # if any values are empty
      if not configname:
         return jsonify(error="Bad Request"), 400

      # if config name is not entered
      if len(configname) < 1:
         return jsonify(error="Invalid config name"), 400

      # if config name already in use
      if configname in (UserConfigurationManager.list_configs()):
         return jsonify(error="Config name in use"), 400

      UserConfigurationManager(configname).create(UserConfigurationManager.get_available_config_name())
      
   return jsonify(success=True), 201, {"HX-Redirect": "/"} # return redirect to index (config editing page)

@routes.route("/api/configremove", methods=['POST'])
@AuthSession.auth_required
def configRemove():
   if request.method == "POST":
      configname = request.json["name"] # take request as JSON
      if UserConfigurationManager(configname).remove():
         return jsonify(success=True), 200
      else:
         return jsonify(success=False), 400

@routes.route('/api/getconfigs', methods=['GET'])
@AuthSession.auth_required
def getUserConfigs():
   configs = {}
   # for every config, fetch config data and append it to a dictionary 
   for configName in UserConfigurationManager.list_configs():
      configs[configName] = UserConfigurationLoader(configName).load_as_dict()
   return jsonify(configs), 200 # return all configs and their data to be handled front-end

@routes.route('/api/updatecurrentconfig', methods=['POST'])
@AuthSession.auth_required
def setCurrentUserConfig():
   configname = request.json["ConfigName"]
   if configname in UserConfigurationManager.list_configs():
      drinkmachine.set_selected_config_name(request.json["ConfigName"]) 
      return jsonify(success=True), 200
   return jsonify(error="Config does not exist"), 400

@routes.route('/api/otp', methods=['GET'])
@AuthSession.auth_required
def getOTP():
   return jsonify({"otp":AuthSession.OTP})

@routes.route('/api/start', methods=['POST'])
@AuthSession.auth_required
def start():
   configNo = request.json["configNo"]
   drinkmachine.start(configNo)
   return jsonify(success=True), 200

@routes.route('/api/stop', methods=['POST'])
@AuthSession.auth_required
def stop():
   drinkmachine.stop()
   return jsonify(success=True), 200

@routes.route('/api/getcartridges', methods=['GET'])
@AuthSession.auth_required
def getCartridges():
   return jsonify(SystemConfigurationLoader().load().get_cartridges()), 200 # return all configs and their data to be handled front-end

