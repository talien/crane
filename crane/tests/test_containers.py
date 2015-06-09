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

    def test_generate_parameters(self):
        expected = "-v a -v b -v c "
        assert container()._generate_parameters("a b c", "-v") == expected
        expected = ""
        assert container()._generate_parameters("", "-v") == expected
