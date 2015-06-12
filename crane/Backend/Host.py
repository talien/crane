from crane.webserver import db
from Models.HostModel import HostModel
import paramiko
import StringIO

class SSHConnection:
    def __init__(self, host):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if not host.username and host.sshkey:
            keybuffer = StringIO.StringIO(host.sshkey)
            pkey = paramiko.PKey.from_private_key(keybuffer)
            self.ssh.connect(host.host, username=host.username, pkey=pkey)
        else:
            self.ssh.connect(host.host, username=host.username, password=host.password)

    def execute(self, command):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(command)
        stdout = ssh_stdout.read()
        stderr = ssh_stderr.read()
        exit_code = ssh_stdout.channel.recv_exit_status()
        return {'stdout': stdout, 'stderr': stderr, 'exit_code': exit_code}

    def put_file(self, filename, content):
        transport = self.ssh.get_transport()
        sftp = paramiko.sftp_client.SFTPClient.from_transport(transport)
        script = sftp.file(filename, "w")
        script.write(content)

class HostProvider:
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
        return HostModel.query.all()

    def query_hosts_with_masked_credentials(self):
        return map(lambda x: self.__use_fingerprint_for_key(x), self.query_hosts())

    def get_host_by_id(self, id):
        host = HostModel.query.filter_by(id=id).first()
        return host

    def get_host_info(self, id):
        host = HostModel.query.filter_by(id=id).first()
        ssh = self.get_connection(host)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker info; docker version")
        info = ssh_stdout.read()
        return info

    def delete_host(self, id):
        host = HostModel.query.filter_by(id=id).first()
        if host:
            db.session.delete(host)
            db.session.commit()

    def __use_fingerprint_for_key(self, host):
        if host.sshkey:
            keybuffer = StringIO.StringIO(host.sshkey)
            pkey = paramiko.RSAKey.from_private_key(keybuffer)
            fingerprint = pkey.get_fingerprint().encode('hex')
            host.sshkey = "FP:" + fingerprint
        return host.to_dict()

    def get_connection(self, host):
        return SSHConnection(host)
