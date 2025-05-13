import json
from flask import request, jsonify

from hardware import *
from .authmanager import AuthManager

from . import AuthSession, routes # import constants from initialiser file

drinkmachine = DrinkMachine(AuthSession.OTP)

@routes.route('/api/authenticate', methods=['GET'])
def authDevice():
   if request.method == 'GET':
      response = AuthSession.authenticate(request.args.get('authcode'), request.remote_addr) # pass OTP authcode into authenticate method
      return response

@routes.route('/api/editconfig', methods=['POST'])
@AuthSession.auth_required
def editConfig():
   if request.method == 'POST':
      if request.form['configSelect'] == "...": # ... is the default option for the select
         return jsonify(error="Must select config"), 400
      
      if None in (request.form['name'], request.form['totalVolume']):
         return jsonify(error="Field values should be populated"), 400
      
      config = UserConfigurationLoader(drinkmachine.get_selected_config_name()).load() # load current user config to be edited

      # edit config's button's keybinds to new entered keybinds
      system_cartridges = SystemConfigurationLoader().load().get_cartridges()

      ratios = (len(request.form) - 4) // 2

      # if request.form['inputTypeSelect'] == "Volume in ML":
      #    calculateRatio = True
      #    denominator = 0
      #    for mixerNumber in range(1, ratios + 1):
      #       value = request.form[f"volumeInput{mixerNumber}"]
      #       if value:
      #          denominator += float(request.form[f"volumeInput{mixerNumber}"])
      # else:
      #    calculateRatio = False

      for mixerNumber in range(1, ratios + 1):
         if mixerNumber > system_cartridges or mixerNumber < 1:
            return jsonify(error="Cartridge number does not exist"), 400
         
         proportion = request.form[f"volumeInput{mixerNumber}"]

         if not proportion:
            continue

        # if not (proportion or) 
         
         value = float(proportion)

         if value <= 0:
            return jsonify(error="Volume must be greater than 0"), 400
         
         config.set_proportion(str(mixerNumber), value)

      # get grid sizes
      name = request.form['name']

      # ensure inputs are digits
      if len(name) < 1:
         return jsonify(error="Must enter a drink name"), 400
      elif name in UserConfigurationManager.list_configs() and name != drinkmachine.get_selected_config_name():
         return jsonify(error="Config name already exists"), 400
      
      config.set_name(name)

      size = int(request.form['totalVolume'])

      if size <= 0:
         return jsonify(error="Total volume cannot be 0"), 400
      
      config.set_default_size(size)

      # overwrite edited config
      UserConfigurationSaver(config).save(drinkmachine.get_selected_config_name())

      return jsonify(success=True), 201, {"HX-Redirect": "/"}

@routes.route("/api/configcreate", methods=['POST'])
@AuthSession.auth_required
def configCreate():
   if request.method == "POST":
      newconfig = request.form

      # get configname and gridsizes from form data
      configname = newconfig.get("configName")

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
      configname = request.json["ConfigName"] # take request as JSON
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

@routes.route('/api/getcartridges', methods=['GET'])
@AuthSession.auth_required
def getCartridges():
   return jsonify(SystemConfigurationLoader().load().get_cartridges()), 200 # return all configs and their data to be handled front-end

