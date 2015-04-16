import paramiko
from flask import jsonify, request
from crane import app, db
import StringIO

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

    def get_connection(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if not self.username and self.sshkey:
            keybuffer = StringIO.StringIO(self.sshkey)
            pkey = paramiko.PKey.from_private_key(keybuffer)
            ssh.connect(self.host, username=self.username, pkey=pkey)
        else:
            ssh.connect(self.host, username=self.username, password=self.password)
        return ssh 

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

def use_fingerprint_for_key(host):
    if host['sshkey']:
        keybuffer = StringIO.StringIO(host['sshkey'])
        pkey = paramiko.RSAKey.from_private_key(keybuffer)
        fingerprint = pkey.get_fingerprint().encode('hex')
        host['sshkey'] = fingerprint
    return host

@app.route('/host', methods=['GET'])
def query_hosts(): 
    hosts = db.session.execute(Host.__table__ .select())
    transformed_hosts = map(lambda x:dict(x), hosts)
    return jsonify(result=map(lambda x:use_fingerprint_for_key(x), transformed_hosts))

@app.route('/host/<id>', methods=['GET'])
def get_host(id):
    host = Host.query.filter_by(id=id).first()
    ssh = host.get_connection()
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker info; docker version")
    info = ssh_stdout.read()
    return jsonify(result=info)

@app.route('/host/<id>', methods=['DELETE'])
def delete_host(id):
    host = Host.query.filter_by(id=id).first()
    if host:
      db.session.delete(host)
      db.session.commit()
    return ""
