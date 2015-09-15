from flask import request, jsonify

from crane.webserver import app
from crane.Backend.HostProvider import HostProvider
from crane.Backend.Utils.SSHConnection import SSHConnection
from crane.Backend.Exceptions import InvalidInputDataException

host = HostProvider(SSHConnection())


@app.route('/host', methods=['POST'])
def add_host():
    try:
        host_id = host.add_host(request.get_json())
        return jsonify(id=host_id)
    except InvalidInputDataException, fields:
        return jsonify(fields), 400


@app.route('/host/<id>', methods=['POST'])
def update_host(id):
    host.update_host(id, request.get_json())
    return ""


@app.route('/host', methods=['GET'])
def query_hosts():
    return jsonify(result=host.query_hosts_with_masked_credentials())


@app.route('/host/<id>', methods=['GET'])
def get_host(id):
    return jsonify(result=host.get_host_info(id))


@app.route('/host/<id>', methods=['DELETE'])
def delete_host(id):
    host.delete_host(id)
    return ""
