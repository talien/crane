from crane.Backend.Interpolator import Interpolator


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


class Deployer(object):

    def __init__(self, host_provider):
        self.host_provider = host_provider

    def deploy(self, host_id, data):
        return self.run_container(host_id, data, foreground=False)

    def task(self, host_id, data):
        return self.run_container(host_id, data, foreground=True)

    def run_container(self, host_id, data, foreground):
        interpolator = Interpolator()
        if data['deploy'] == 'raw':
            container = interpolator.interpolate_variables(data['container'], {})
        else:
            container = interpolator.interpolate_variables(data['template']['deploy'], data['parameters'])
        predeploy = self.__run_deploy_hook(host_id, container, "predeploy")
        if predeploy['exit_code'] != 0:
            return DeployError(message="Predeploy script failed!", predeploy=predeploy)
        deploy = self.host_provider.run_command_on_host_id(host_id, "docker run {9} --name {0} {1} {2} {3} {4} {5} {6} {7} {8}".format(
            container['name'],
            container['volumes'],
            container['capabilities'],
            container['hostname'],
            container['environment'],
            container['portmapping'],
            container['restart'],
            container['image'],
            container['command'],
            "-d" if not foreground else ""))
        if deploy['exit_code'] != 0:
            return DeployError(message="Starting container failed!", predeploy=predeploy, deploy=deploy)
        postdeploy = self.__run_deploy_hook(host_id, container, "postdeploy")
        if postdeploy['exit_code'] != 0:
            return DeployError(message="Postdeploy script failed!", predeploy=predeploy, deploy=deploy, postdeploy=postdeploy)
        return DeploySuccess(container=deploy['stdout'].strip())

    def __run_deploy_hook(self, host_id, container, hook):
        result = {'stdout': "", 'stderr': "", 'exit_code': 0}
        if hook in container:
            self.host_provider.put_file_on_host_id(host_id, "/tmp/script", container[hook])
            result = self.host_provider.run_command_on_host_id(host_id, "/bin/bash /tmp/script")
        return result
