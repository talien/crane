class MockSSH:

    def __init__(self, expectations):
        self.expectations = expectations
        self.command_index = 0

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


class MockProvider:

    def __init__(self, ssh=None):
        self.ssh = ssh

    def get_host_by_id(self, hostid):
        return None

    def get_connection(self, host):
        return self.ssh
