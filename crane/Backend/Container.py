import json

from crane.utils import parallel_map_reduce


class Container:

    def __init__(self, host_provider):
        self.host_provider = host_provider

    def get_containers(self):
        hosts = self.host_provider.query_hosts()
        result = parallel_map_reduce(
            lambda x: self.__get_container_from_host(x), lambda x, y: x + y, hosts, [])
        result.sort(key=lambda x: x['name'])
        return result

    def remove_container(self, host_id, container_id):
        self._run_command_on_host(host_id, "docker rm {0}".format(container_id))

    def inspect_container(self, host_id, container_id):
        data = self._run_command_on_host(host_id, "docker inspect {0}".format(container_id))['stdout']
        return json.loads(data)[0]

    def start_container(self, host_id, container_id):
        self._run_command_on_host(host_id, "docker start {0}".format(container_id))

    def stop_container(self, host_id, container_id):
        self._run_command_on_host(host_id, "docker stop {0}".format(container_id))

    def get_container_logs(self, host_id, container_id, tail):
        data = self._run_command_on_host(host_id, "docker logs --tail={1} {0}".format(container_id, tail))['stdout']
        return data

    def _run_command_on_host(self, host_id, command):
        return self.host_provider.run_command_on_host_id(host_id, command)

    def _get_container_command(self, container):
        if container['Config']['Cmd']:
            result = " ".join(container['Config']['Cmd'])
        else:
            result = "None"
        return result

    def _get_container_state(self, container):
        if container['State']['Running']:
            result = 'Running'
        else:
            result = 'Stopped'
        return result

    def _get_info_from_container(self, container, host):
        return {'id': container['Id'],
                'name': container['Name'],
                'image': container['Config']['Image'],
                'cmd': self._get_container_command(container),
                'state': self._get_container_state(container),
                'hostid': host.id,
                'hostname': host.name}

    def __get_container_list(self, host):
        containers = []
        command_result = self.host_provider.run_command_on_host(host, "docker ps -a -q")['stdout']
        if command_result:
            containers = command_result.rstrip().split("\n")
        return containers

    def get_number_of_containers(self, host):
        containers = self.__get_container_list(host)
        return len(containers)

    def __get_container_from_host(self, host):
        container_list = []
        containers = self.__get_container_list(host)
        if containers:
            container_params = " ".join(containers)
            inspections = self.host_provider.run_command_on_host(host, "docker inspect {0}".format(container_params))['stdout']
            container_list = map(lambda x: self._get_info_from_container(x, host), json.loads(inspections))
        return container_list
