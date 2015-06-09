from crane.Backend.Host import HostProvider
from crane.utils import parallel_map_reduce
import json

host_provider = HostProvider()

class Container:

    def __init__(self):
        pass

    def get_containers(self):
        hosts = host_provider.query_hosts()
        result = parallel_map_reduce(
            lambda x: self.__get_container_from_host(x), lambda x, y: x + y, hosts, [])
        result.sort(key=lambda x: x['name'])
        return result

    def remove_container(self, host_id, container_id):
        host = host_provider.get_host_by_id(host_id)
        ssh = host_provider.get_connection(host)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
            "docker rm {0}".format(container_id))

    def inspect_container(self, host_id, container_id):
        host = host_provider.get_host_by_id(host_id)
        ssh = host_provider.get_connection(host)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
            "docker inspect {0}".format(container_id))
        data = ssh_stdout.read()
        return json.loads(data)[0]

    def start_container(self, host_id, container_id):
        host = host_provider.get_host_by_id(host_id)
        ssh = host_provider.get_connection(host)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
            "docker start {0}".format(container_id))

    def stop_container(self, host_id, container_id):
        host = host_provider.get_host_by_id(host_id)
        ssh = host_provider.get_connection(host)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
            "docker stop {0}".format(container_id))

    def get_container_logs(self, host_id, container_id, tail):
        host = host_provider.get_host_by_id(host_id)
        ssh = host_provider.get_connection(host)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
            "docker logs --tail={1} {0}".format(container_id, tail))
        data = ssh_stdout.read()
        return data

    def _get_info_from_container(self, container, host):
        result = {}
        result['id'] = container['Id']
        result['name'] = container['Name']
        result['image'] = container['Config']['Image']
        if container['Config']['Cmd']:
            result['cmd'] = " ".join(container['Config']['Cmd'])
        else:
            result['cmd'] = "None"
        if container['State']['Running']:
            result['state'] = 'Running'
        else:
            result['state'] = 'Stopped'
        result['hostid'] = host.id
        result['hostname'] = host.name
        return result

    def __get_container_from_host(self, host):
        ssh = host_provider.get_connection(host)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker ps -a -q")
        result = ssh_stdout.read()
        if result == "":
            return []
        containers = result.split("\n")
        container_params = " ".join(containers)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
            "docker inspect {0}".format(container_params))
        result = ssh_stdout.read()
        container_list = map(
            lambda x: self._get_info_from_container(x, host), json.loads(result))
        return container_list
