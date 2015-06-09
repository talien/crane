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
