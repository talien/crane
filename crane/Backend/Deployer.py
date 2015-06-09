class DeployResult(object):

    def __init__(self, status):
        self.result = {}
        self.result["status"] = status


class DeployError(DeployResult):

    def __init__(self, message, predeploy="", deploy="", postdeploy=""):
        super(DeployError, self).__init__("error")
        self.result['message'] = message
        self.result['predeploy'] = predeploy
        self.result['deploy'] = deploy
        self.result['postdeploy'] = postdeploy


class DeploySuccess(DeployResult):

    def __init__(self, container):
        super(DeploySuccess, self).__init__("success")
        self.result['container'] = container


class Deployer:

    def __init__(self, host_provider):
        self.host_provider = host_provider

    def deploy(self, host_id, data):
        host = self.host_provider.get_host_by_id(host_id)
        ssh = self.host_provider.get_connection(host)
        if data['deploy'] == 'raw':
            container = self.__interpolate_variables(data['container'], {})
        else:
            container = self.__interpolate_variables(
                data['template']['deploy'], data['parameters'])
        predeploy = self.__run_deploy_hook(ssh, container, "predeploy")
        if predeploy['exit_code'] != 0:
            return DeployError(message="Predeploy script failed!", predeploy=predeploy)
        deploy = ssh.execute("docker run -d -name {0} {1} {2} {3} {4} {5} {6} {7} {8}".format(
            container['name'],
            container['volumes'],
            container['capabilities'],
            container['hostname'],
            container['environment'],
            container['portmapping'],
            container['restart'],
            container['image'],
            container['command']))
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
        if 'predeploy' in deploy:
            container['predeploy'] = self.__interpolate_string(deploy['predeploy'], parameters)
        if 'postdeploy' in deploy:
            container['postdeploy'] = self.__interpolate_string(deploy['postdeploy'], parameters)
        return container

    def __run_deploy_hook(self, ssh, container, hook):
        if not (hook in container):
            return {'stdout': "", 'stderr': "",'exit_code': 0}
        ssh.put_file("/tmp/script", container['predeploy'])
        result = ssh.execute("/bin/bash /tmp/script")
        return result
