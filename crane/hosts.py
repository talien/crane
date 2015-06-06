import paramiko
from flask import jsonify, request
from webserver import app, db
import StringIO
from Backend.Models.HostModel import HostModel


@app.route('/host', methods=['POST'])
def add_host():
    json = request.get_json()
    host = HostModel(json['name'],
                json['host'],
                json['username'],
                json['password'] if json.has_key('password') else "",
                json['sshkey'] if json.has_key('sshkey') else "",
               )
    db.session.add(host)
    db.session.commit()
    return ""


@app.route('/host/<id>', methods=['POST'])
def update_host(id):
    json = request.get_json()
    host = HostModel.query.filter_by(id=id).first()
    host.name = json['name']
    host.host = json['host']
    host.username = json['username']
    host.password = json['password'] if json.has_key('password') else ""
    host.sshkey = json['sshkey'] if json.has_key('sshkey') and (json['sshkey'][:3] != "FP:") else ""
    db.session.add(host)
    db.session.commit()
    return ""

def use_fingerprint_for_key(host):
    if host['sshkey']:
        keybuffer = StringIO.StringIO(host['sshkey'])
        pkey = paramiko.RSAKey.from_private_key(keybuffer)
        fingerprint = pkey.get_fingerprint().encode('hex')
        host['sshkey'] = "FP:" + fingerprint
    return host

@app.route('/host', methods=['GET'])
def query_hosts():
    hosts = db.session.execute(HostModel.__table__ .select())
    transformed_hosts = map(lambda x:dict(x), hosts)
    return jsonify(result=map(lambda x:use_fingerprint_for_key(x), transformed_hosts))

@app.route('/host/<id>', methods=['GET'])
def get_host(id):
    host = HostModel.query.filter_by(id=id).first()
    ssh = host.get_connection()
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker info; docker version")
    info = ssh_stdout.read()
    return jsonify(result=info)

@app.route('/host/<id>', methods=['DELETE'])
def delete_host(id):
    host = HostModel.query.filter_by(id=id).first()
    if host:
      db.session.delete(host)
      db.session.commit()
    return ""


def get_connection(host):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if not host.username and host.sshkey:
        keybuffer = StringIO.StringIO(host.sshkey)
        pkey = paramiko.PKey.from_private_key(keybuffer)
        ssh.connect(host.host, username=host.username, pkey=pkey)
    else:
        ssh.connect(host.host, username=host.username, password=host.password)
    return ssh