from webserver import app, db
import requests
from flask import jsonify, request
from crane.Backend.DockerHub import DockerHub
from crane.Backend.DockerPrivate import DockerPrivate


class Registry(db.Model):
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

    def get_provider(self):
        if self.provider == 'dockerhub':
            return DockerHub(self.url, self.username, self.password, requests)
        elif self.provider == 'private':
            return DockerPrivate(self.url, self.username, self.password, requests)


def expand_results_with_registry_name(results, registry):
    for result in results:
        result['registry'] = registry.name
        result['registry_id'] = registry.id
    return results


@app.route("/registry", methods=[ "GET" ])
def get_registries():
    registries = db.session.execute(Registry.__table__ .select())
    transformed_registries = map(lambda x:dict(x), registries)
    return jsonify(result=transformed_registries)


@app.route("/registry", methods=[ "POST" ])
def add_registry():
    json = request.get_json()
    registry = Registry(
                  json['name'],
                  json['url'],
                  json.get('username',""),
                  json.get('password',""),
                  json['provider'])
    db.session.add(registry)
    db.session.commit()
    return ""


@app.route("/registry/<registry_id>", methods=["DELETE"])
def delete_registry(registry_id):
    registry = Registry.query.filter_by(id=registry_id).first()
    if registry:
        db.session.delete(registry)
        db.session.commit()
    return ""


@app.route("/registry/<registry_id>/repository/<namespace>/<repo_name>/tags")
@app.route("/registry/<registry_id>/repository/<repo_name>/tags", defaults={'namespace': ''})
def get_tags(registry_id, namespace, repo_name):
    if namespace != "":
        repo_name = "{0}/{1}".format(namespace, repo_name)
    registry = Registry.query.filter_by(id=registry_id).first()
    provider = registry.get_provider()
    result = provider.tags(repo_name)
    return jsonify(result=result)


@app.route("/registry/<registry_id>/repository/<namespace>/<repo_name>/image/<image_id>")
@app.route("/registry/<registry_id>/repository/<repo_name>/image/<image_id>", defaults={'namespace': ''})
def get_image(registry_id, namespace, repo_name, image_id):
    if namespace != "":
        repo_name = "{0}/{1}".format(namespace, repo_name)
    registry = Registry.query.filter_by(id=registry_id).first()
    provider = registry.get_provider()
    result = provider.image(repo_name, image_id)
    return jsonify(result=result)


@app.route("/search", methods=[ "GET"])
def search_registry():
    query = request.args.get("q")
    registries = Registry.query.all()
    results = []
    for registry in registries:
        provider = registry.get_provider()
        results = results + expand_results_with_registry_name(provider.search(query), registry)
    return jsonify(result=results)
