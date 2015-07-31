from crane.webserver import app
from flask import jsonify, request
from crane.Backend.HostProvider import HostProvider

from crane.Backend.Task import Tasks
from crane.Backend.Utils.SSHConnection import SSHConnection

host_provider = HostProvider(SSHConnection())
tasker = Tasks(host_provider)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    tasker.create(data)
    return ""

@app.route("/tasks", methods=['GET'])
def get_tasks():
    result = tasker.query()
    return jsonify(result=result)

@app.route("/tasks/<id>/stop", methods=['POST'])
def stop_task(id):
    result = tasker.stop(id)
    return ""

@app.route("/tasks/<id>/logs", methods=['GET'])
def get_task_logs(id):
    result = tasker.logs(id)
    return result

@app.route("/tasks/<id>", methods=['DELETE'])
def remove_task(id):
    result = tasker.remove(id)
    return ""
