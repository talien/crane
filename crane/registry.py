from webserver import app, db
import requests
from flask import jsonify, request
import json
import concurrent.futures

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
           return DockerHub(self.url, self.username, self.password)
        elif self.provider == 'private':
           return DockerPrivate(self.url, self.username, self.password)

class DockerHub:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def search(self, query):

        def query_page(query, page, url):
            res = requests.get("{2}/v1/search?q={0}&page={1}".format(query, page, self.url), verify=False)
            result = json.loads(res.text)
            return result['results']

        num_page = 1000;
        actual_page = 1
        results = []
        res = requests.get("{2}/v1/search?q={0}&page={1}".format(query, actual_page, self.url), verify=False)
        result = json.loads(res.text)
        results = results + result['results']
        num_pages = result['num_pages']
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for page in range(2,num_pages + 1):
                futures.append(executor.submit(query_page, query, page, self.url))
        for f in concurrent.futures.as_completed(futures):
            results = results + f.result()
        results.sort(key=lambda x:x['star_count'], reverse=True)
        return results

class DockerPrivate:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def search(self, query):
        res = requests.get("{1}/v1/search?q={0}".format(query, self.url), verify=False)
        result = json.loads(res.text)
        results = result['results']
        return results

def expand_results_with_registry_name(results, registry):
    for result in results:
        result['registry'] = registry
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

@app.route("/search", methods=[ "GET"])
def search_registry():
    query = request.args.get("q")
    registries = Registry.query.all()
    results = []
    for registry in registries:
        provider = registry.get_provider()
        results = results + expand_results_with_registry_name(provider.search(query), registry.name)
    return jsonify(result=results)
