from crane.webserver import app
from crane.Backend.HostProvider import HostProvider
import crane.hosts
import json


class TestHosts:
    def test_query_hosts(self):
        host_provider = HostProvider("")
        data = {
            'name': 'Csillamponi',
            'host': 'crane.gov',
            'username': 'Bela',
            'password': 'encrypted'
        }
        data2 = {
            'name': 'Nyancat',
            'host': 'crane.xxx',
            'username': 'Geza',
            'password': 'unencrypted'
        }
        host_id_1 = host_provider.add_host(data)
        host_id_2 = host_provider.add_host(data2)
        tester_app = app.test_client()
        response = tester_app.get('/host')
        assert response.status_code == 200
        data['id'] = 1
        data2['id'] = 2
        data['sshkey'] = ''
        data2['sshkey'] = ''
        assert json.loads(response.data) == {'result': [data, data2]}
        host_provider.delete_host(host_id_1)
        host_provider.delete_host(host_id_2)
