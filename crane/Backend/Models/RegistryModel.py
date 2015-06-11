from crane.webserver import db


class RegistryModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    url = db.Column(db.String(1024))
    username = db.Column(db.String(256))
    password = db.Column(db.String(1024))
    provider = db.Column(db.String(32))

    def __init__(self, name, url, username, password, provider):
        self.name = name
        self.url = url
        self.username = username
        self.password = password
        self.provider = provider
