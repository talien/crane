from crane.Backend.Host import HostProvider
from crane.utils import parallel_map_reduce
from crane.Backend.Deployer import DeploySuccess, DeployError
import paramiko
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

    def deploy_container(self, host_id, data):
        host = host_provider.get_host_by_id(host_id)
        ssh = host_provider.get_connection(host)
        if data['deploy'] == 'raw':
            container = self.__interpolate_variables(data['container'], {})
        else:
            container = self.__interpolate_variables(
                data['template']['deploy'], data['parameters'])
        predeploy = self.__run_deploy_hook(ssh, container, "predeploy")
        if predeploy['exit_code'] != 0:
            return DeployError(message="Predeploy script failed!", predeploy=predeploy)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("docker run -d -name {0} {1} {2} {3} {4} {5} {6} {7} {8}".format(
            container['name'],
            container['volumes'],
            container['capabilities'],
            container['hostname'],
            container['environment'],
            container['portmapping'],
            container['restart'],
            container['image'],
            container['command']))
        deploy = {'stdout': ssh_stdout.read(),
                  'stderr': ssh_stderr.read(),
                  'exit_code': ssh_stdout.channel.recv_exit_status()}
        if deploy['exit_code'] != 0:
            return DeployError(message="Starting container failed!", predeploy=predeploy, deploy=deploy)
        postdeploy = self.__run_deploy_hook(ssh, container, "postdeploy")
        if postdeploy['exit_code'] != 0:
            return DeployError(message="Postdeploy script failed!", predeploy=predeploy, deploy=deploy, postdeploy=postdeploy)
        return DeploySuccess(container=deploy['stdout'].strip())

    def _generate_parameters(self, parameters, parameter_name):
        return "".join(["{0} {1} ".format(parameter_name, param) for param in parameters.split()])

    def __interpolate_string(self, string, params):
        has_work = True
        result = ""
        while has_work:
            start = string.find("%(")
            if start == -1:
                result += string
                has_work = False
            else:
                end = string.find(")%", start)
                if end == -1:
                    result += string
                    has_work = False
                else:
                    param = string[start + 2:end]
                    result += string[0:start]
                    value = params.get(param, "")
                    result += value
                    string = string[end + 2:]
        return result

    def __interpolate_array(self, array, params):
        return [self.__interpolate_string(item, params) for item in array]

    def __interpolate_variables(self, deploy, parameters):
        container = {}
        container['environment'] = self._generate_parameters(self.__interpolate_string(
            deploy['environment'], parameters), "-e") if 'environment' in deploy else ""
        container['portmapping'] = self._generate_parameters(self.__interpolate_string(
            deploy['portmapping'], parameters), "-p") if 'portmapping' in deploy else ""
        container['volumes'] = self._generate_parameters(self.__interpolate_string(
            deploy['volumes'], parameters), "-v") if 'volumes' in deploy else ""
        container['capabilities'] = self._generate_parameters(self.__interpolate_string(
            deploy['capabilities'], parameters), "--cap-add") if 'capabilities' in deploy else ""
        container[
            'restart'] = "--restart={0}".format(deploy['restart']) if 'restart' in deploy else ""
        container['command'] = self.__interpolate_string(
            deploy['command'], parameters) if 'command' in deploy else ""
        container['name'] = self.__interpolate_string(
            deploy['name'], parameters)
        container['image'] = self.__interpolate_string(
            deploy['image'], parameters)
        container['hostname'] = "--hostname={0}".format(self.__interpolate_string(
            deploy['hostname'], parameters)) if 'hostname' in deploy else ""
        container['predeploy'] = self.__interpolate_string(
            deploy['predeploy'], parameters) if 'predeploy' in deploy else ""
        container['postdeploy'] = self.__interpolate_string(
            deploy['postdeploy'], parameters) if 'postdeploy' in deploy else ""
        return container

    def __run_deploy_hook(self, ssh, container, hook):
        if 'predeploy' not in container:
            return ""
        transport = ssh.get_transport()
        sftp = paramiko.sftp_client.SFTPClient.from_transport(transport)
        script = sftp.file("/tmp/script", "w")
        script.write(container['predeploy'])
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
            "/bin/bash /tmp/script")
        stdout = ssh_stdout.read()
        stderr = ssh_stderr.read()
        exit_code = ssh_stdout.channel.recv_exit_status()
        return {'stdout': stdout, 'stderr': stderr, 'exit_code': exit_code}

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
