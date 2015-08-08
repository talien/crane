from crane.webserver import app
from flask import jsonify, request
from Backend.Environments import EnvironmentProvider
from Backend.Deployer import Deployer
from Backend.HostProvider import HostProvider
from crane.Backend.Utils.SSHConnection import SSHConnection

host_provider = HostProvider(SSHConnection())
environment_provider = EnvironmentProvider(host_provider)

@app.route("/environment", methods=['GET'])
def get_environments():
    return jsonify(result=environment_provider.get_environments())

@app.route("/environment", methods=['POST'])
def add_environment():
    json = request.get_json()
    env_id = environment_provider.add_environment(json['name'])
    return jsonify(id=env_id)

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

@app.route("/environment/<id>/deploy", methods=['POST'])
def deploy_in_environment(id):
    data = request.get_json()
    count = data['count']
    hosts = environment_provider.get_hosts_for_deployment(id, count)
    deployer = Deployer(host_provider)
    name = data['container']['name']
    count = 1
    for host in hosts:
        data['container']['name'] = "{0}-{1}".format(name, count)
        result = deployer.deploy(host, data)
        count = count + 1
    return ""
