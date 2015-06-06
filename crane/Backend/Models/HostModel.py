from crane.webserver import db


class HostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    host = db.Column(db.String(1024))
    username = db.Column(db.String(256))
    password = db.Column(db.String(1024))
    sshkey = db.Column(db.Text())

    def __init__(self, name, host, username, password, sshkey):
        self.name = name
        self.host = host
        self.username = username
        self.password = password
        self.sshkey = sshkey

    def __repr__(self):
        return '<User %r>' % self.username