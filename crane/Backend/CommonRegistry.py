class CommonRegistry(object):
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def search(self):
        raise NotImplementedError()

    def image(self):
        raise NotImplementedError()

    def tags(self):
        raise NotImplementedError()