from webserver import app, db
import requests
from requests.auth import HTTPBasicAuth
from flask import jsonify, request
import json
from utils import parallel_map_reduce


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


class CommonRegistry(object):
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password


class DockerHub(CommonRegistry):
    def __init__(self, url, username, password, requests):
        super(DockerHub, self).__init__(url, username, password)
        self.requests = requests

    def query_tags(self, reponame):
        res = self.requests.get("{1}/v1/repositories/{0}/tags".format(reponame, self.url), verify=False)
        tags = json.loads(res.text)
        return tags

    def search(self, query):

        def query_page(query, page, url):
            res = self.requests.get("{2}/v1/search?q={0}&page={1}".format(query, page, url), verify=False)
            result = json.loads(res.text)
            return result['results']

        actual_page = 1
        results = []
        response = self.requests.get("{2}/v1/search?q={0}&page={1}".format(query, actual_page, self.url), verify=False)
        result = json.loads(response.text)
        results = results + result['results']
        num_pages = result['num_pages']
        results = parallel_map_reduce(lambda x: query_page(query, x, self.url), lambda x, y: x+y, range(2, num_pages + 1), results)
        results.sort(key=lambda x: x['star_count'], reverse=True)
        return results

    def tags(self, reponame):
        def add_tag(images, image, tag):
            if not images.has_key(image):
                images[image] = []
            images[image].append(tag)
            return images

        tags = self.query_tags(reponame)
        (_, _, images) = self.query_images(reponame)
        image_map = {}
        for image in images:
            image_map[image['id'][0:8]] = image['id']
        images = {}
        for tag in tags:
            if image_map.has_key(tag['layer']):
                result = add_tag(images, image_map[tag['layer']], tag['name'])
        result = []
        for k, v in images.iteritems():
            result.append({'name': k, 'tags': v})
        return result

    def query_images(self, reponame):
        headers = {'X-Docker-Token': 'true'}
        res = self.requests.get("{1}/v1/repositories/{0}/images".format(reponame, self.url), headers=headers, verify=False)
        token = res.headers['x-docker-token']
        endpoint = res.headers['x-docker-endpoints']
        image_list = json.loads(res.text)
        return (token, endpoint, image_list)

    def query_image(self, image_id, endpoint, token):
        headers = {'Authorization': 'Token {0}'.format(token)}
        res = self.requests.get("https://{0}/v1/images/{1}/json".format(endpoint, image_id), headers=headers, verify=False)
        image_detail = json.loads(res.text)
        return image_detail

    def image(self, reponame, image):
        def reduce_func(images, image):
            images[image['id']] = image
            return images
        (token, endpoint, image_list) = self.query_images(reponame)
        headers = {'Authorization': 'Token {0}'.format(token)}
        res = self.requests.get("https://{0}/v1/images/{1}/ancestry".format(endpoint, image), headers=headers, verify=False)
        ancestors = json.loads(res.text)
        images = parallel_map_reduce(lambda x: self.query_image(x, endpoint, token), reduce_func, ancestors, {})
        result = []
        for i in ancestors:
            result.append(images[i])
        return result


class DockerPrivate(CommonRegistry):
    def __init__(self, url, username, password, requests):
        super(DockerPrivate, self).__init__(url, username, password)
        self.requests = requests

    def request(self, url):
        if self.username:
            res = self.requests.get(url, verify=False, auth=HTTPBasicAuth(self.username, self.password))
        else:
            res = self.requests.get(url, verify=False)
        return res

    def query_tags(self, reponame):
        res = self.request("{1}/v1/repositories/{0}/tags".format(reponame, self.url))
        tags = json.loads(res.text)
        return tags

    def search(self, query):
        res = self.request("{1}/v1/search?q={0}".format(query, self.url))
        result = json.loads(res.text)
        results = result['results']
        return results

    def tags(self, reponame):
        def add_tag(images, image, tag):
            if not images.has_key(image):
                images[image] = []
            images[image].append(tag)
            return images

        tags = self.query_tags(reponame)
        images = {}
        for k,v in tags.iteritems():
            images = add_tag(images, v, k)
        result = []
        for k,v in images.iteritems():
            result.append({'name':k,'tags':v})
        return result

    def image(self, reponame, image):
        res = self.request("{0}/v1/images/{1}/ancestry".format(self.url, image))
        ancestors = json.loads(res.text)
        result = []
        for i in ancestors:
            res = self.request("{0}/v1/images/{1}/json".format(self.url, i))
            result.append(json.loads(res.text))
        return result


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
