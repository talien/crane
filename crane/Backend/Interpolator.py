class Interpolator(object):
    def __init__(self):
        pass

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

    def __generate_parameters(self, parameters, parameter_name):
        return "".join(["{0} {1} ".format(parameter_name, param) for param in parameters.split()])

    def __make_container_item(self, deploy, parameters, itemname, switch):
        return self.__generate_parameters(self.__interpolate_string(
            deploy[itemname], parameters), switch) if itemname in deploy else ""

    def interpolate_variables(self, deploy, parameters):
        container = {}
        container['environment'] = self.__make_container_item(deploy, parameters, "environment", "-e")
        container['portmapping'] = self.__make_container_item(deploy, parameters, "portmapping", "-p")
        container['volumes'] = self.__make_container_item(deploy, parameters, "volumes", "-v")
        container['capabilities'] = self.__make_container_item(deploy, parameters, "capabilities", "--cap-add")
        container['restart'] = "--restart={0}".format(deploy['restart']) if 'restart' in deploy else ""
        container['command'] = self.__interpolate_string(deploy['command'], parameters) if 'command' in deploy else ""
        container['name'] = self.__interpolate_string(deploy['name'], parameters)
        container['image'] = self.__interpolate_string(deploy['image'], parameters)
        container['hostname'] = "--hostname={0}".format(self.__interpolate_string(
            deploy['hostname'], parameters)) if 'hostname' in deploy else ""
        if 'predeploy' in deploy:
            container['predeploy'] = self.__interpolate_string(deploy['predeploy'], parameters)
        if 'postdeploy' in deploy:
            container['postdeploy'] = self.__interpolate_string(deploy['postdeploy'], parameters)
        return container