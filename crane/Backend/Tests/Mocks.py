class Response:
    def __init__(self, text, headers):
        self.text = text
        self.headers = headers


class requestsMock(object):
    def __init__(self, expectations):
        self.expectations = expectations

    def get(self, url, **kwargs):
        return Response(self.expectations[url]['response'], self.expectations[url]['headers'])


class MockSSH(object):
    def __init__(self, expectations):
        self.expectations = expectations
        self.command_index = 0

    def get_connection(self, host):
        return self

    def execute(self, command):
        assert self.expectations[self.command_index]['type'] == 'execute'
        assert self.expectations[self.command_index]['command'] == command
        if 'result' in self.expectations[self.command_index]:
            result = self.expectations[self.command_index]['result']
        else:
            result = {'stdout': 'alma', 'stderr': '', 'exit_code': 0}
        self.command_index = self.command_index + 1
        return result

    def put_file(self, file, content):
        assert self.expectations[self.command_index]['type'] == 'put_file'
        assert self.expectations[self.command_index]['file'] == file
        assert self.expectations[self.command_index]['content'] == content
        self.command_index = self.command_index + 1


class MockProvider(object):

    def __init__(self, ssh=None):
        self.ssh = ssh

    def run_command_on_host_id(self, host_id, command):
        return self.ssh.execute(command)

    def run_command_on_host(self, host, command):
        return self.ssh.execute(command)

    def put_file_on_host_id(self, host_id, file, contents):
        return self.ssh.put_file(file, contents)


class MockHost(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name