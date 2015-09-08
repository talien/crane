import json

from crane.Backend.CommonRegistry import CommonRegistry
from crane.utils import parallel_map_reduce


class DockerHub(CommonRegistry):
    def __init__(self, url, username, password, requests):
        super(DockerHub, self).__init__(url, username, password)
        self.requests = requests

    def _query_tags(self, reponame):
        res = self.requests.get("{1}/v1/repositories/{0}/tags".format(reponame, self.url), verify=False)
        tags = json.loads(res.text)
        return tags

    def _query_page(self, query, page_number, url):
        res = self.requests.get("{2}/v1/search?q={0}&page={1}".format(query, page_number, url), verify=False)
        result = json.loads(res.text)
        return result

    def __query_page_results(self, query, page_number, url):
        return self._query_page(query, page_number, url)['results']

    def search(self, query):
        results = []
        result = self._query_page(query, 1, self.url)
        results = results + result['results']
        num_pages = result['num_pages']
        results = parallel_map_reduce(lambda x: self.__query_page_results(query, x, self.url), lambda x, y: x+y, range(2, num_pages + 1), results)
        results.sort(key=lambda x: x['star_count'], reverse=True)
        return results

    def tags(self, reponame):
        tags = self._query_tags(reponame)
        (_, _, images) = self.__query_images(reponame)

        image_map = {image['id'][0:8]: image['id'] for image in images}

        images = {}
        for tag in tags:
            if tag['layer'] in image_map:
                images.setdefault(image_map[tag['layer']], []).append(tag['name'])

        result = [{'name': k, 'tags': v} for k, v in images.iteritems()]
        return result

    def __query_images(self, reponame):
        headers = {'X-Docker-Token': 'true'}
        res = self.requests.get("{1}/v1/repositories/{0}/images".format(reponame, self.url), headers=headers, verify=False)
        token = res.headers['x-docker-token']
        endpoint = res.headers['x-docker-endpoints']
        image_list = json.loads(res.text)
        return (token, endpoint, image_list)

    def __query_image(self, image_id, endpoint, token):
        headers = {'Authorization': 'Token {0}'.format(token)}
        res = self.requests.get("https://{0}/v1/images/{1}/json".format(endpoint, image_id), headers=headers, verify=False)
        image_detail = json.loads(res.text)
        return image_detail

    def image(self, reponame, image):
        def reduce_func(images, image):
            images[image['id']] = image
            return images
        (token, endpoint, image_list) = self.__query_images(reponame)
        headers = {'Authorization': 'Token {0}'.format(token)}
        res = self.requests.get("https://{0}/v1/images/{1}/ancestry".format(endpoint, image), headers=headers, verify=False)
        ancestors = json.loads(res.text)
        images = parallel_map_reduce(lambda x: self.__query_image(x, endpoint, token), reduce_func, ancestors, {})
        result = []
        for i in ancestors:
            result.append(images[i])
        return result