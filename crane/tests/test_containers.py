from crane.containers import get_info_from_container

class Host:
    id = 42
    name = 'csillamponi'

class TestContainers:
    def test_get_info_from_container(self):
        container = {
            'Id' : 'almafa',
            'Name' : 'kortefa',
            'Config' : {
                'Image' : 'mogyorofa',
                'Cmd' : ['diofa']
                },
            'State' : {
                'Running' : True
                }
        }
        host = Host()

        result = {
            'id' : 'almafa',
            'name' : 'kortefa',
            'image' : 'mogyorofa',
            'cmd' : 'diofa',
            'state' : 'Running',
            'hostid' : 42,
            'hostname' : 'csillamponi'
        }

        assert get_info_from_container(container, host) == result

        container['State']['Running'] = False
        result['state'] = 'Stopped'

        assert get_info_from_container(container, host) == result
