from flask import request
from webserver import app
from Backend.Host import Host

host = Host()


@app.route('/host', methods=['POST'])
def add_host():
    host.add_host(request.get_json())
    return ""


@app.route('/host/<id>', methods=['POST'])
def update_host(id):
    host.update_host(id, request.get_json())
    return ""


@app.route('/host', methods=['GET'])
def query_hosts():
    return host.query_hosts()


@app.route('/host/<id>', methods=['GET'])
def get_host(id):
    return host.get_host(id)


@app.route('/host/<id>', methods=['DELETE'])
def delete_host(id):
    host.delete_host(id)
    return ""