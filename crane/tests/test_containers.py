from crane.Backend.Container import Container
import pytest

@pytest.fixture
def container():
    return Container()

class Host:
    id = 42
    name = 'csillamponi'

class TestContainers:
    def test_get_info_from_container(self):
        container_map = {
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
        host = Host()

        result = {
            'id': 'almafa',
            'name': 'kortefa',
            'image': 'mogyorofa',
            'cmd': 'diofa',
            'state': 'Running',
            'hostid': 42,
            'hostname': 'csillamponi'
        }

        assert container()._get_info_from_container(container_map, host) == result

        container_map['State']['Running'] = False
        result['state'] = 'Stopped'

        assert container()._get_info_from_container(container_map, host) == result

        container_map['Config']['Cmd'] = ""
        result['cmd'] = "None"

        assert container()._get_info_from_container(container_map, host) == result
