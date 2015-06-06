from crane.webserver import db
from Models.HostModel import HostModel
from flask import jsonify
import paramiko
import StringIO


class Host:
    def __init__(self):
        pass

    def add_host(self, data):
        host = HostModel(data['name'],
                         data['host'],
                         data['username'],
                         data['password'] if 'password' in data else "",
                         data['sshkey'] if 'sshkey' in data else "", )
        db.session.add(host)
        db.session.commit()

    def update_host(self, id, data):
        host = HostModel.query.filter_by(id=id).first()
        host.name = data['name']
        host.host = data['host']
        host.username = data['username']
        host.password = data['password'] if 'password' in data else ""
        host.sshkey = data['sshkey'] if 'sshkey' in data and (data['sshkey'][:3] != "FP:") else ""
        db.session.add(host)
        db.session.commit()

    def query_hosts(self):
        hosts = db.session.execute(HostModel.__table__ .select())
        transformed_hosts = map(lambda x: dict(x), hosts)
        return jsonify(result=map(lambda x: self.__use_fingerprint_for_key(x), transformed_hosts))

    def get_host(self, id):
        host = HostModel.query.filter_by(id=id).first()
        ssh = self.get_connection(host)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker info; docker version")
        info = ssh_stdout.read()
        return jsonify(result=info)

    def delete_host(self, id):
        host = HostModel.query.filter_by(id=id).first()
        if host:
            db.session.delete(host)
            db.session.commit()

    def __use_fingerprint_for_key(self, host):
        if host['sshkey']:
            keybuffer = StringIO.StringIO(host['sshkey'])
            pkey = paramiko.RSAKey.from_private_key(keybuffer)
            fingerprint = pkey.get_fingerprint().encode('hex')
            host['sshkey'] = "FP:" + fingerprint
        return host

    def get_connection(self, host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if not host.username and host.sshkey:
            keybuffer = StringIO.StringIO(host.sshkey)
            pkey = paramiko.PKey.from_private_key(keybuffer)
            ssh.connect(host.host, username=host.username, pkey=pkey)
        else:
            ssh.connect(host.host, username=host.username, password=host.password)
        return ssh