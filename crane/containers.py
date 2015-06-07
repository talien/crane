from webserver import app
from flask import jsonify, Response, request
from Backend.Host import Host
from Backend.Container import Container

host_instance = Host()
container_instance = Container()


@app.route('/container', methods=['GET'])
def get_containers():
    return container_instance.get_containers()


@app.route('/host/<host_id>/container/<container_id>', methods=['DELETE'])
def remove_container(host_id, container_id):
    container_instance.remove_container(host_id, container_id)
    return ""


@app.route('/host/<host_id>/container/<container_id>', methods=['GET'])
def inspect_container(host_id, container_id):
    return container_instance.inspect_container(host_id, container_id)


@app.route('/host/<host_id>/container/<container_id>/start', methods=['POST'])
def start_container(host_id, container_id):
    container_instance.start_container(host_id, container_id)
    return ""


@app.route('/host/<host_id>/container/<container_id>/stop', methods=['POST'])
def stop_container(host_id, container_id):
    container_instance.stop_container(host_id, container_id)
    return ""


@app.route('/host/<host_id>/container/<container_id>/lastlog', methods=['GET'])
def get_container_lastlog(host_id, container_id):
    data = container_instance.get_container_logs(host_id, container_id, 200)
    return jsonify(result=data)


@app.route('/host/<host_id>/container/<container_id>/fulllog', methods=['GET'])
def get_container_fulllog(host_id, container_id):
    data = container_instance.get_container_logs(host_id, container_id, "all")
    return Response(data, content_type='text/plain')


@app.route('/host/<host_id>/container', methods=['POST'])
def deploy_container(host_id):
    return container_instance.deploy_container(host_id, request.get_json())