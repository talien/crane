from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template, send_from_directory, request, jsonify
import subprocess
import paramiko
import json

app = Flask(__name__, static_url_path='')
app.debug = True
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    host = db.Column(db.String(1024))
    username = db.Column(db.String(256))
    password = db.Column(db.String(1024))
    sshkey = db.Column(db.Text())

    def __init__(self, name, host, username, password, sshkey):
        self.name = name
        self.host = host
        self.username = username
        self.password = password
        self.sshkey = sshkey

    def __repr__(self):
        return '<User %r>' % self.username  

@app.route('/host', methods=['POST'])
def add_host():
    json = request.get_json()
    host = Host(json['name'],
                json['host'],
                json['username'],
                json['password'] if json.has_key('password') else "",
                json['sshkey'] if json.has_key('sshkey') else "",
               )
    db.session.add(host)
    db.session.commit()
    return ""
   
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/host', methods=['GET'])
def query_hosts(): 
    return jsonify(result=map(lambda x:dict(x),db.session.execute(Host.__table__ .select())))

@app.route('/host/<id>', methods=['DELETE'])
def delete_host(id):
    host = Host.query.filter_by(id=id).first()
    if host:
      db.session.delete(host)
      db.session.commit() 
    return ""

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
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host.host, username=host.username, password=host.password)
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
    for host in hosts:
        result = result + get_container_from_host(host)
    return jsonify(result=result)

@app.route('/host/<host_id>/container/<container_id>', methods=['DELETE'])
def remove_container(host_id, container_id):
    host = Host.query.filter_by(id=host_id).first()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host.host, username=host.username, password=host.password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker rm {0}".format(container_id))
    return ""

@app.route('/host/<host_id>/container/<container_id>/start', methods=['POST'])
def start_container(host_id, container_id):
    host = Host.query.filter_by(id=host_id).first()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host.host, username=host.username, password=host.password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker start {0}".format(container_id))
    return ""

@app.route('/host/<host_id>/container/<container_id>/stop', methods=['POST'])
def stop_container(host_id, container_id):
    host = Host.query.filter_by(id=host_id).first()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host.host, username=host.username, password=host.password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker stop {0}".format(container_id))
    return ""

@app.route('/host/<host_id>/container', methods=['POST'])
def deploy_container(host_id):
    json = request.get_json()
    host = Host.query.filter_by(id=host_id).first()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host.host, username=host.username, password=host.password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker run -d -name {0} {1}".format(json['name'],json['image']))
    ssh_stdout.read()
    return ""

@app.route("/")
def index():
    return render_template("hello.jade", render_template=render_template)

if __name__ == "__main__":
    app.run()


