import json
from requests.auth import HTTPBasicAuth
from crane.Backend.CommonRegistry import CommonRegistry

class DockerPrivate(CommonRegistry):
    def __init__(self, url, username, password, requests):
        super(DockerPrivate, self).__init__(url, username, password)
        self.requests = requests

    def __request(self, url):
        if self.username:
            res = self.requests.get(url, verify=False, auth=HTTPBasicAuth(self.username, self.password))
        else:
            res = self.requests.get(url, verify=False)
        return res

    def __query_tags(self, reponame):
        res = self.__request("{1}/v1/repositories/{0}/tags".format(reponame, self.url))
        tags = json.loads(res.text)
        return tags

    def search(self, query):
        res = self.__request("{1}/v1/search?q={0}".format(query, self.url))
        result = json.loads(res.text)
        results = result['results']
        return results

    def tags(self, reponame):
        tags = self.__query_tags(reponame)
        images = {}
        for k, v in tags.iteritems():
            images.setdefault(v, []).append(k)
        result = [{'name': k, 'tags': v} for k, v in images.iteritems()]
        return result

    def image(self, reponame, image):
        res = self.__request("{0}/v1/images/{1}/ancestry".format(self.url, image))
        ancestors = json.loads(res.text)
        result = []
        for i in ancestors:
            res = self.__request("{0}/v1/images/{1}/json".format(self.url, i))
            result.append(json.loads(res.text))
        return result