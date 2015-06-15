from Models.EnvironmentModel import EnvironmentModel, hosts_env
from Container import Container
from Host import HostProvider
from sqlalchemy.sql import and_
from crane.webserver import db

class EnvironmentProvider():
    def __init__(self, host_provider):
        self.host_provider = host_provider

    def get_environments(self):
        environments = EnvironmentModel.query.all()
        result = []
        for environment in environments:
            hosts = map( lambda x: { 'name': x.name, 'id':x.id}, environment.hosts)
            result.append({ 'name': environment.name, 'hosts': hosts, 'id': environment.id})
        return result

    def add_environment(self, name):
        environment = EnvironmentModel(name)
        db.session.add(environment)
        db.session.commit()

    def add_host_to_environment(self, env_id, host_id):
        insert = hosts_env.insert().values(env_id=env_id,hosts_id=host_id)
        db.session.execute(insert)
        db.session.commit()

    def delete_host_from_environment(self, env_id, host_id):
        delete = hosts_env.delete().where(and_(hosts_env.c.env_id == env_id,hosts_env.c.hosts_id == host_id))
        res = db.session.execute(delete)
        db.session.commit()

    def delete_environment(self, env_id):
        environment = EnvironmentModel.query.filter_by(id=env_id).first();
        if len(environment.hosts) != 0:
            return
        db.session.delete(environment)
        db.session.commit()

    def get_hosts_for_deployment(self, env_id, host_count):
        environment = EnvironmentModel.query.filter_by(id=env_id).first();
        container = Container(self.host_provider)
        hosts = [{'id':host.id,'count':container.get_number_of_containers(host)} for host in environment.hosts]
        result = []
        hosts = sorted(hosts, key=lambda x:x['count'])
        for i in xrange(0,host_count):
            result = result + [hosts[0]['id']]
            hosts[0]['count'] += 1
            hosts = sorted(hosts, key=lambda x:x['count'])
        return result
