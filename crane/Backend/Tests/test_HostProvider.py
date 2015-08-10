import pytest
from crane.Backend.HostProvider import HostProvider
from crane.Backend.Tests.Mocks import MockSSH
from crane.webserver import db


@pytest.fixture(scope='session', autouse=True)
def clear_db():
    db.drop_all()
    db.create_all()


@pytest.fixture
def host_provider(mockssh):
    return HostProvider(mockssh)


class TestHostProvider:
    def test_run_command_on_host(self):
        sshmock = MockSSH([{'type': 'execute',
                            'command': 'docker almafa',
                            'result': {'stdout': 'kortefa', 'stderr': '', 'exit_code': 0}}])
        result = host_provider(sshmock).run_command_on_host("a_host", "docker almafa")
        assert result == {'stdout': 'kortefa', 'stderr': '', 'exit_code': 0}

    def test_add_host(self):
        dummymock = ''
        data = {
            'name': 'Csillamponi',
            'host': 'crane.gov',
            'username': 'Bela',
            'password': 'encrypted'
        }
        host_id = host_provider(dummymock).add_host(data)
        host = host_provider(dummymock).get_host_by_id(host_id)
        assert host.name == 'Csillamponi'
        assert host.host == 'crane.gov'
        assert host.username == 'Bela'
        assert host.password == 'encrypted'
        assert host.sshkey == ''
        host_provider(dummymock).delete_host(host_id)
        del data['password']
        data['sshkey'] = 'secret_key'
        host_id = host_provider(dummymock).add_host(data)
        host = host_provider(dummymock).get_host_by_id(host_id)
        assert host.password == ''
        assert host.sshkey == 'secret_key'
        host_provider(dummymock).delete_host(host_id)

    def test_update_host(self):
        dummymock = ''
        data = {
            'name': 'Csillamponi',
            'host': 'crane.gov',
            'username': 'Bela',
            'password': 'encrypted'
        }
        host_id = host_provider(dummymock).add_host(data)
        data2 = {
            'name': 'Csillamponi2',
            'host': 'crane.gov2',
            'username': 'Bela2',
            'password': 'encrypted2'
        }
        host_provider(dummymock).update_host(host_id, data2)
        host = host_provider(dummymock).get_host_by_id(host_id)
        assert host.name == 'Csillamponi2'
        assert host.host == 'crane.gov2'
        assert host.username == 'Bela2'
        assert host.password == 'encrypted2'
        assert host.sshkey == ''
        del data2['password']
        data2['sshkey'] = 'some_ssh_key'
        host_provider(dummymock).update_host(host_id, data2)
        host = host_provider(dummymock).get_host_by_id(host_id)
        assert host.sshkey == 'some_ssh_key'
        host_provider(dummymock).delete_host(host_id)

    def test_delete_host(self):
        dummymock = ''
        data = {
            'name': 'Csillamponi',
            'host': 'crane.gov',
            'username': 'Bela',
            'password': 'encrypted'
        }
        host_id = host_provider(dummymock).add_host(data)
        assert host_provider(dummymock).get_host_by_id(host_id) is not None
        host_provider(dummymock).delete_host(host_id)
        assert host_provider(dummymock).get_host_by_id(host_id) is None

    def test_get_host_info(self):
        sshmock = MockSSH([{'type': 'execute',
                            'command': 'docker info; docker version',
                            'result': {'stdout': 'some_info', 'stderr': '', 'exit_code': 0}}])
        result = host_provider(sshmock).get_host_info('some_id')
        assert result == 'some_info'

    def test_query_hosts(self):
        dummymock = ''
        data = {
            'name': 'Csillamponi',
            'host': 'crane.gov',
            'username': 'Bela',
            'password': 'encrypted'
        }
        assert len(host_provider(dummymock).query_hosts()) == 0
        host_provider(dummymock).query_hosts()
        host_id_1 = host_provider(dummymock).add_host(data)
        host_id_2 = host_provider(dummymock).add_host(data)
        assert len(host_provider(dummymock).query_hosts()) == 2
        host_provider(dummymock).delete_host(host_id_1)
        host_provider(dummymock).delete_host(host_id_2)
        assert len(host_provider(dummymock).query_hosts()) == 0

    def test_put_file_on_host_id(self):
        sshmock = MockSSH([{'type': 'put_file',
                            'content': 'korbacs',
                            'file': '/tmp/script'}])
        host_provider(sshmock).put_file_on_host_id('1', '/tmp/script', 'korbacs')

    def test_query_hosts_with_masked_credentials(self):
        with open('crane/Backend/Tests/Data/private.key') as keyfile:
            sshkey = keyfile.read()
        dummymock = ''
        data = {
            'name': 'Csillamponi',
            'host': 'crane.gov',
            'username': 'Bela',
            'sshkey': sshkey
        }
        host_id = host_provider(dummymock).add_host(data)
        host = host_provider(dummymock).get_host_by_id(host_id)
        assert host.sshkey[:3] != 'FP:'
        queried_hosts =  host_provider(dummymock).query_hosts_with_masked_credentials()
        assert queried_hosts[0]['sshkey'][:3] == 'FP:'
        host_provider(dummymock).delete_host(host_id)
