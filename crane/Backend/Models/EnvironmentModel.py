from crane.webserver import db

hosts_env = db.Table('hosts_env',
    db.Column('hosts_id', db.Integer, db.ForeignKey('host_model.id')),
    db.Column('env_id', db.Integer, db.ForeignKey('environment_model.id'))
)

class EnvironmentModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    hosts = db.relationship('HostModel', secondary=hosts_env,
       backref=db.backref('envs', lazy='dynamic'))

    def __init__(self, name):
        self.name = name
