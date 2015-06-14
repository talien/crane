from crane.Backend.Deployer import Deployer
import pytest


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

mock_provider = MockProvider()


@pytest.fixture
def deployer():
    return Deployer(mock_provider)


class TestDeployer:

    def test_generate_parameters(self):
        expected = "-v a -v b -v c "
        assert deployer()._generate_parameters("a b c", "-v") == expected
        expected = ""
        assert deployer()._generate_parameters("", "-v") == expected

    def test_deploy(self):
        mock_provider.ssh = MockSSH(
            [{'type': 'execute', 'command': "docker run -d -name alma       redis "}])
        res = deployer().deploy(
            1, {'deploy': 'raw', 'container': {'name': 'alma', 'image': 'redis'}})
        assert res.result == {'status': 'success', 'container': 'alma'}

    def test_pre_deploy(self):
        mock_provider.ssh = MockSSH([{'type': 'put_file', 'content': 'kakukk', 'file': '/tmp/script'},
                                     {'type': 'execute',
                                         'command': '/bin/bash /tmp/script'},
                                     {'type': 'execute', 'command': "docker run -d -name alma       redis "}])
        res = deployer().deploy(1, {'deploy': 'raw', 'container': {
            'name': 'alma', 'image': 'redis', 'predeploy': 'kakukk'}})
        assert res.result == {'status': 'success', 'container': 'alma'}

    def test_post_deploy(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': "docker run -d -name alma       redis "},
                                     {'type': 'put_file', 'content': 'kakukk',
                                         'file': '/tmp/script'},
                                     {'type': 'execute', 'command': '/bin/bash /tmp/script'}])
        res = deployer().deploy(1, {'deploy': 'raw', 'container': {
            'name': 'alma', 'image': 'redis', 'postdeploy': 'kakukk'}})
        assert res.result == {'status': 'success', 'container': 'alma'}

    def test_template_deploy(self):
        mock_provider.ssh = MockSSH(
            [{'type': 'execute', 'command': "docker run -d -name korte       redis "}])
        res = deployer().deploy(1, {'deploy': 'template', 'template': {'deploy': {
            'name': '%(alma)%', 'image': 'redis'}}, 'parameters': {'alma': 'korte'}})
        assert res.result == {'status': 'success', 'container': 'alma'}

    def test_template_deploy_with_unclosed_variable(self):
        mock_provider.ssh = MockSSH(
            [{'type': 'execute', 'command': "docker run -d -name %(alma       redis "}])
        res = deployer().deploy(1, {'deploy': 'template', 'template': {'deploy': {
            'name': '%(alma', 'image': 'redis'}}, 'parameters': {'alma': 'korte'}})
        assert res.result == {'status': 'success', 'container': 'alma'}

    def test_pre_deploy_fail(self):
        mock_provider.ssh = MockSSH([{'type': 'put_file', 'content': 'kakukk', 'file': '/tmp/script'},
                                     {'type': 'execute',
                                         'command': '/bin/bash /tmp/script', 'result' : {'stdout': 'alma', 'stderr': '', 'exit_code': 1}},
                                     {'type': 'execute', 'command': "docker run -d -name alma       redis "}])
        res = deployer().deploy(1, {'deploy': 'raw', 'container': {
            'name': 'alma', 'image': 'redis', 'predeploy': 'kakukk'}})
        assert res.result == {'status': 'error',
                              'message': 'Predeploy script failed!',
                              'deploy':'',
                              'postdeploy': '',
                              'predeploy': {'exit_code': 1, 'stderr': '', 'stdout': 'alma'}}

    def test_deploy_fail(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': "docker run -d -name alma       redis ", 'result':{'stdout': 'alma', 'stderr': '', 'exit_code': 1} }])
        res = deployer().deploy(1, {'deploy': 'raw', 'container': {
            'name': 'alma', 'image': 'redis'}})
        assert res.result == {'status': 'error',
                              'message': 'Starting container failed!',
                              'deploy':{'exit_code': 1, 'stderr': '', 'stdout': 'alma'},
                              'postdeploy': '',
                              'predeploy': {'exit_code': 0, 'stderr': '', 'stdout': ''}}

    def test_post_deploy_fail(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': "docker run -d -name alma       redis "},
                                     {'type': 'put_file', 'content': 'kakukk',
                                         'file': '/tmp/script'},
                                     {'type': 'execute', 'command': '/bin/bash /tmp/script', 'result': {'stdout': 'alma', 'stderr': '', 'exit_code': 1}}])
        res = deployer().deploy(1, {'deploy': 'raw', 'container': {
            'name': 'alma', 'image': 'redis', 'postdeploy': 'kakukk'}})
        assert res.result == {'status': 'error',
                              'message': 'Postdeploy script failed!',
                              'deploy':{'exit_code': 0, 'stderr': '', 'stdout': 'alma'},
                              'postdeploy': {'exit_code': 1, 'stderr': '', 'stdout': 'alma'},
                              'predeploy': {'exit_code': 0, 'stderr': '', 'stdout': ''}}
