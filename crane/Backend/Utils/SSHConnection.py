import StringIO
import paramiko


class SSHConnection(object):
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def get_connection(self, host):
        if not host.username and host.sshkey:
            keybuffer = StringIO.StringIO(host.sshkey)
            pkey = paramiko.PKey.from_private_key(keybuffer)
            self.ssh.connect(host.host, username=host.username, pkey=pkey)
        else:
            self.ssh.connect(host.host, username=host.username, password=host.password)
        return self

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
