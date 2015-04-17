from crane import app
from hosts import Host
from flask import jsonify, Response, request
import json
import concurrent.futures
import paramiko

def get_info_from_container(container, host):
    result = {}
    result['id'] = container['Id']
    result['name'] = container['Name']
    result['image'] = container['Config']['Image']
    result['cmd'] = " ".join(container['Config']['Cmd'])
    if container['State']['Running']:
       result['state'] = 'Running'
    else:
       result['state'] = 'Stopped'
    result['hostid'] = host.id
    result['hostname'] = host.name
    return result

def get_container_from_host(host):
    ssh = host.get_connection()
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker ps -a -q")
    result = ssh_stdout.read()
    if result == "":
       return []
    containers = result.split("\n")
    container_params = " ".join(containers)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker inspect {0}".format(container_params))
    result = ssh_stdout.read()
    container_list = map( lambda x: get_info_from_container(x, host), json.loads(result))
    return container_list

@app.route('/container', methods=['GET'])
def get_containers():
    result = []
    hosts = Host.query.all()
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for host in hosts:
            futures.append(executor.submit(get_container_from_host, host))
    for f in concurrent.futures.as_completed(futures):
        result = result + f.result()
    result.sort(key=lambda x:x['name'])
    return jsonify(result=result)

@app.route('/host/<host_id>/container/<container_id>', methods=['DELETE'])
def remove_container(host_id, container_id):
    host = Host.query.filter_by(id=host_id).first()
    ssh = host.get_connection()
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker rm {0}".format(container_id))
    return ""

@app.route('/host/<host_id>/container/<container_id>', methods=['GET'])
def inspect_container(host_id, container_id):
    host = Host.query.filter_by(id=host_id).first()
    ssh = host.get_connection()
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker inspect {0}".format(container_id))
    data = ssh_stdout.read()
    return jsonify(result=json.loads(data)[0])

@app.route('/host/<host_id>/container/<container_id>/start', methods=['POST'])
def start_container(host_id, container_id):
    host = Host.query.filter_by(id=host_id).first()
    ssh = host.get_connection()
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker start {0}".format(container_id))
    return ""

@app.route('/host/<host_id>/container/<container_id>/stop', methods=['POST'])
def stop_container(host_id, container_id):
    host = Host.query.filter_by(id=host_id).first()
    ssh = host.get_connection()
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker stop {0}".format(container_id))
    return ""

def get_container_logs(host_id, container_id, tail):
    host = Host.query.filter_by(id=host_id).first()
    ssh = host.get_connection()
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker logs --tail={1} {0}".format(container_id, tail))
    data = ssh_stdout.read()
    return data

@app.route('/host/<host_id>/container/<container_id>/lastlog', methods=['GET'])
def get_container_lastlog(host_id, container_id):
    data = get_container_logs(host_id, container_id, 200);
    return jsonify(result=data)

@app.route('/host/<host_id>/container/<container_id>/fulllog', methods=['GET'])
def get_container_fulllog(host_id, container_id):
    data = get_container_logs(host_id, container_id, "all");
    return Response(data, content_type='text/plain')

def generate_environment_params(envs):
    envs = envs.split()
    result = ""
    for env in envs:
      result = result + "-e {0} ".format(env)
    return result

def generate_portmapping_params(ports):
    ports = ports.split()
    result = ""
    for port in ports:
      result = result + "-p {0} ".format(port)
    return result

def generate_volume_params(volumes):
    volumes=volumes.split()
    result = ""
    for volume in volumes:
      result = result + "-v {0} ".format(volume)
    return result

def generate_capabilities_params(caps):
    caps = caps.split()
    result = ""
    for cap in caps:
      result = result + "--cap-add {0} ".format(cap)
    return result

def interpolate_string(string, params):
    has_work = True
    result = ""
    while (has_work):
      start = string.find("%(")
      if start == -1:
         result += string
         has_work = False
      else:
         end = string.find(")%", start)
         if end == -1:
            result += string
            has_work = False
         else:
            param = string[start+2:end]
            result += string[0:start]
            value = params.get(param, "")
            result += value
            string = string[end+2:]
    return result

def interpolate_array(array, params):
    result = []
    for item in array:
        result.append(interpolate_string(item, params))
    return result

def interpolate_variables(deploy, parameters):
    container = {}
    container['environment'] = generate_environment_params(interpolate_string(deploy['environment'], parameters)) if deploy.has_key('environment') else ""
    container['portmapping'] = generate_portmapping_params(interpolate_string(deploy['portmapping'], parameters)) if deploy.has_key('portmapping') else ""
    container['volumes'] = generate_volume_params(interpolate_string(deploy['volumes'], parameters)) if deploy.has_key('volumes') else ""
    container['capabilities'] = generate_capabilities_params(interpolate_string(deploy['capabilities'], parameters)) if deploy.has_key('capabilities') else ""
    container['restart'] = "--restart={0}".format(deploy['restart']) if deploy.has_key('restart') else ""
    container['command'] = interpolate_string(deploy['command'], parameters) if deploy.has_key('command') else ""
    container['name'] = interpolate_string(deploy['name'], parameters)
    container['image'] = interpolate_string(deploy['image'], parameters)
    container['hostname'] = "--hostname={0}".format(interpolate_string(deploy['hostname'], parameters)) if deploy.has_key('hostname') else ""
    container['predeploy'] = interpolate_string(deploy['predeploy'], parameters) if deploy.has_key('predeploy') else ""
    container['postdeploy'] = interpolate_string(deploy['postdeploy'], parameters) if deploy.has_key('postdeploy') else ""
    return container

def run_deploy_hook(ssh, container, hook):
    if not container.has_key('predeploy'):
       return ""
    transport = ssh.get_transport()
    sftp = paramiko.sftp_client.SFTPClient.from_transport(transport)
    script = sftp.file("/tmp/script", "w")
    script.write(container['predeploy'])
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("/bin/bash /tmp/script")
    stdout = ssh_stdout.read()
    stderr = ssh_stderr.read()
    exit_code = ssh_stdout.channel.recv_exit_status()
    return { 'stdout': stdout, 'stderr' : stderr, 'exit_code': exit_code }

@app.route('/host/<host_id>/container', methods=['POST'])
def deploy_container(host_id):
    json = request.get_json()
    host = Host.query.filter_by(id=host_id).first()
    ssh = host.get_connection()
    container = {};
    if json['deploy'] == 'raw':
       container = interpolate_variables(json['container'], {})
    else:
       container = interpolate_variables(json['template']['deploy'], json['parameters'])
    predeploy = run_deploy_hook(ssh, container, "predeploy")
    if predeploy['exit_code'] != 0:
        return jsonify(predeploy=predeploy, status="error", message="Predeploy script failed!")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker run -d -name {0} {1} {2} {3} {4} {5} {6} {7} {8}".format(
            container['name'],
            container['volumes'],
            container['capabilities'],
            container['hostname'],
            container['environment'],
            container['portmapping'],
            container['restart'],
            container['image'],
            container['command']
        ))
    deploy = {}
    deploy['stdout'] = ssh_stdout.read()
    deploy['stderr'] = ssh_stderr.read()
    deploy['exit_code'] = ssh_stdout.channel.recv_exit_status()
    if deploy['exit_code'] != 0:
        return jsonify(predeploy=predeploy, deploy=deploy, status="error", message="Starting container failed!")
    postdeploy = run_deploy_hook(ssh, container, "postdeploy")
    if postdeploy['exit_code'] != 0:
        return jsonify(predeploy=predeploy, deploy=deploy, postdeploy=postdeploy, status="error", message="Postdeploy script failed!")
    return jsonify(status="success", container=deploy['stdout'].strip())
