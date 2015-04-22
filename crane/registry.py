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

class CommonRegistry(object):
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def query_tags(self, reponame):
        res = requests.get("{1}/v1/repositories/{0}/tags".format(reponame, self.url), verify=False)
        tags = json.loads(res.text)
        return tags

class DockerHub(CommonRegistry):

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
            #result.append({'name':tag['name'],'image':image_map[tag['layer']]})
            result = add_tag(images, image_map[tag['layer']], tag['name'])
        result = []
        for k,v in images.iteritems():
            result.append({'name':k,'tags':v})
        return result

    def query_images(self, reponame):
        headers = {'X-Docker-Token':'true'}
        res = requests.get("{1}/v1/repositories/{0}/images".format(reponame, self.url), headers=headers, verify=False)
        token = res.headers['x-docker-token']
        endpoint = res.headers['x-docker-endpoints']
        image_list = json.loads(res.text)
        return (token, endpoint, image_list)

    def images(self, reponame):
        def query_image(image_id, endpoint, token):
            headers = {'Authorization':'Token {0}'.format(token)}
            res = requests.get("https://{0}/v1/images/{1}/json".format(endpoint, image_id), headers=headers, verify=False)
            image_detail = json.loads(res.text)
            return image_detail

        tags = self.query_tags(reponame)
        print "Tags: {0}".format(len(tags))
        (token, endpoint, image_list) = self.query_images(reponame)
        print "Images: {0}".format(len(image_list))
        images = {}
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            for image in image_list[:100]:
                futures.append(executor.submit(query_image, image['id'], endpoint, token))
        i = 0
        for f in concurrent.futures.as_completed(futures):
            image = f.result()
            images[image['id']] = image
            i = i + 1
            print "{0}/{1}".format(i, len(image_list))
        print res.headers
        return {'tags':tags, 'images': images}

    def image(self, reponame, image):
        (token, endpoint, image_list) = self.query_images(reponame)
        headers = {'Authorization':'Token {0}'.format(token)}
        res = requests.get("https://{0}/v1/images/{1}/ancestry".format(endpoint, image), headers=headers, verify=False)
        ancestors = json.loads(res.text)
        result = []
        for i in ancestors:
            res = requests.get("https://{0}/v1/images/{1}/json".format(endpoint, i), headers=headers, verify=False)
            result.append(json.loads(res.text))
        return result


class DockerPrivate(CommonRegistry):

    def search(self, query):
        res = requests.get("{1}/v1/search?q={0}".format(query, self.url), verify=False)
        result = json.loads(res.text)
        results = result['results']
        return results

    def images(self, reponame):
        tags = self.query_tags(reponame)
        if tags.has_key('error'):
            return {}
        res = requests.get("{0}/v1/repositories/{1}/images".format(self.url, reponame), verify=False)
        image_list = json.loads(res.text)
        images = {}
        for image in image_list:
            res = requests.get("{0}/v1/images/{1}/json".format(self.url, image['id']), verify=False)
            image_detail = json.loads(res.text)
            images[image['id']] = image_detail
        return {'tags':tags, 'images': images}

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
        res = requests.get("{0}/v1/images/{1}/ancestry".format(self.url, image), verify=False)
        ancestors = json.loads(res.text)
        result = []
        for i in ancestors:
            res = requests.get("{0}/v1/images/{1}/json".format(self.url, i), verify=False)
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

@app.route("/registry/<registry_id>/repository/<namespace>/<repo_name>")
@app.route("/registry/<registry_id>/repository/<repo_name>", defaults={'namespace':''})
def get_images(registry_id, namespace, repo_name):
    if namespace != "":
        repo_name = "{0}/{1}".format(namespace, repo_name)
    registry = Registry.query.filter_by(id=registry_id).first()
    provider = registry.get_provider()
    result = provider.images(repo_name)
    return jsonify(result=result)

@app.route("/registry/<registry_id>/repository/<namespace>/<repo_name>/tags")
@app.route("/registry/<registry_id>/repository/<repo_name>/tags", defaults={'namespace':''})
def get_tags(registry_id, namespace, repo_name):
    if namespace != "":
        repo_name = "{0}/{1}".format(namespace, repo_name)
    registry = Registry.query.filter_by(id=registry_id).first()
    provider = registry.get_provider()
    result = provider.tags(repo_name)
    return jsonify(result=result)

@app.route("/registry/<registry_id>/repository/<namespace>/<repo_name>/image/<image_id>")
@app.route("/registry/<registry_id>/repository/<repo_name>/image/<image_id>", defaults={'namespace':''})
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
