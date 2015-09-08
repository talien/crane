import json
import pytest

from crane.Backend.Container import Container
from crane.Backend.Tests.Mocks import MockProvider, MockSSH, MockHost


def query_hosts():
    return [MockHost(id=42, name="csillamponi")]

mock_provider = MockProvider()
mock_provider.query_hosts = query_hosts

@pytest.fixture
def container():
    return Container(mock_provider)


def create_container_map():
    return {
        'Id': 'almafa',
        'Name': 'kortefa',
        'Config': {
            'Image': 'mogyorofa',
            'Cmd': ['diofa']
            },
        'State': {
            'Running': True
            }
    }


def create_result():
    return {
        'id': 'almafa',
        'name': 'kortefa',
        'image': 'mogyorofa',
        'cmd': 'diofa',
        'state': 'Running',
        'hostid': 42,
        'hostname': 'csillamponi'
    }


class TestContainers(object):
    def test_get_info_from_container(self):
        container_map = create_container_map()
        host = MockHost(id=42, name='csillamponi')

        result = create_result()

        assert container()._get_info_from_container(container_map, host) == result

        container_map['State']['Running'] = False
        result['state'] = 'Stopped'

        assert container()._get_info_from_container(container_map, host) == result

        container_map['Config']['Cmd'] = ""
        result['cmd'] = "None"

        assert container()._get_info_from_container(container_map, host) == result

    def test_get_containers_from_host(self):
        container_str = json.dumps([create_container_map()])
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': 'docker ps -a -q', 'result': {'stdout': 'alma', 'stderr': '', 'exit_code': 0}},
                                     {'type': 'execute', 'command': 'docker inspect alma', 'result': {'stdout': container_str, 'stderr': '', 'exit_code': 0}}])
        res = container().get_containers()
        assert res == [create_result()]

    def test_get_containers_from_host_where_no_containers_present(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': 'docker ps -a -q', 'result': {'stdout': '', 'stderr': '', 'exit_code': 0}}])
        res = container().get_containers()
        assert res == []

    def test_get_number_of_containers(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': 'docker ps -a -q', 'result': {'stdout': 'alma\nkorte\nbarack\n', 'stderr': '', 'exit_code': 0}}])
        assert container().get_number_of_containers(1) == 3

    def test_remove_container(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': 'docker rm alma', 'result': {'stdout': '', 'stderr': '', 'exit_code': 0}}])
        res = container().remove_container(1, 'alma')

    def test_start_container(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': 'docker start alma', 'result': {'stdout': '', 'stderr': '', 'exit_code':0}}])
        res = container().start_container(1, 'alma')

    def test_stop_container(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': 'docker stop alma', 'result': {'stdout': '', 'stderr': '', 'exit_code': 0}}])
        res = container().stop_container(1, 'alma')

    def test_get_log_from_container(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': 'docker logs --tail=20 alma', 'result': {'stdout': 'korte', 'stderr': '', 'exit_code':0}}])
        res = container().get_container_logs(1, 'alma', 20)
        assert res == "korte"

    def test_inspect_container(self):
        mock_provider.ssh = MockSSH([{'type': 'execute', 'command': 'docker inspect alma', 'result': {'stdout': '[{"alma": "korte"}]', 'stderr': '', 'exit_code':0}}])
        res = container().inspect_container(1, 'alma')
        assert res == {'alma': 'korte'}
