from webserver import app, db
from flask import jsonify, request
from sqlalchemy.sql import and_

hosts_env = db.Table('hosts_env',
    db.Column('hosts_id', db.Integer, db.ForeignKey('host.id')),
    db.Column('env_id', db.Integer, db.ForeignKey('environment.id'))
)

class Environment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    hosts = db.relationship('Host', secondary=hosts_env,
       backref=db.backref('envs', lazy='dynamic'))

    def __init__(self, name):
        self.name = name


@app.route("/environment", methods=['GET'])
def environment():
    environments = Environment.query.all()
    result = []
    for environment in environments:
        hosts = map( lambda x: { 'name': x.name, 'id':x.id}, environment.hosts)
        result.append({ 'name': environment.name, 'hosts': hosts, 'id': environment.id})
    return jsonify(result=result)

@app.route("/environment", methods=['POST'])
def add_environment():
    json = request.get_json()
    environment = Environment(json['name'])
    db.session.add(environment)
    db.session.commit()
    return ""

@app.route("/environment/<id>/host", methods=['POST'])
def add_host_to_environment(id):
    json = request.get_json()
    insert = hosts_env.insert().values(env_id=id,hosts_id=json['id'])
    db.session.execute(insert)
    db.session.commit()
    return ""

@app.route("/environment/<id>/host/<hostid>", methods=['DELETE'])
def delete_host_from_environment(id, hostid):
    delete = hosts_env.delete().where(and_(hosts_env.c.env_id == id,hosts_env.c.hosts_id == hostid))
    res = db.session.execute(delete)
    db.session.commit()
    return ""

@app.route("/environment/<id>", methods=['DELETE'])
def delete_environment(id):
    environment = Environment.query.filter_by(id=id).first();
    if len(environment.hosts) != 0:
        return "Not empty environment"
    db.session.delete(environment)
    db.session.commit()
    return ""
