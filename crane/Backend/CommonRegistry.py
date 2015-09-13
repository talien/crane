class CommonRegistry(object):
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def search(self, query):
        raise NotImplementedError()

    def image(self, reponame, image):
        raise NotImplementedError()

    def tags(self, reponame):
        raise NotImplementedError()
