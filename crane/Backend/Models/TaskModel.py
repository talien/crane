from datetime import datetime

from crane.webserver import db


class TaskModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    host_id = db.Column(db.String(1024))
    container_name = db.Column(db.String(256))
    state = db.Column(db.String(16))
    started = db.Column(db.DateTime())
    finished = db.Column(db.DateTime())

    def __init__(self, name, host_id, container_name):
        self.name = name
        self.host_id = host_id
        self.container_name = container_name
        self.state = "RUNNING"
        self.started = datetime.now()
