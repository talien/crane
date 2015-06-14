from crane.webserver import app
from flask import jsonify, request
from Backend.Environments import EnvironmentProvider

environment_provider = EnvironmentProvider()

@app.route("/environment", methods=['GET'])
def get_environments():
    return jsonify(result=environment_provider.get_environments())

@app.route("/environment", methods=['POST'])
def add_environment():
    json = request.get_json()
    environment_provider.add_environment(json['name'])
    return ""

@app.route("/environment/<id>/host", methods=['POST'])
def add_host_to_environment(id):
    json = request.get_json()
    environment_provider.add_host_to_environment(id, json['id'])
    return ""

@app.route("/environment/<id>/host/<hostid>", methods=['DELETE'])
def delete_host_from_environment(id, hostid):
    environment_provider.delete_host_from_environment(id, hostid)
    return ""

@app.route("/environment/<id>", methods=['DELETE'])
def delete_environment(id):
    environment_provider.delete_environment(id)
    return ""
