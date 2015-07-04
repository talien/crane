from webserver import app
from flask import jsonify, Response, request
from Backend.Host import HostProvider

from Backend.Task import Tasks

tasker = Tasks(HostProvider())

@app.route('/task', methods=['POST'])
def create_task():
    data = request.get_json()
    tasker.create(data)
    return ""

@app.route("/task", methods=['GET'])
def get_tasks():
    result = tasker.query()
    return jsonify(result=result)

@app.route("/task/<id>/stop", methods=['POST'])
def stop_task(id):
    result = tasker.stop(id)
    return ""

@app.route("/task/<id>/logs", methods=['GET'])
def get_task_logs(id):
    result = tasker.logs(id)
    return result

@app.route("/task/<id>", methods=['DELETE'])
def remove_task(id):
    result = tasker.remove(id)
    return ""
