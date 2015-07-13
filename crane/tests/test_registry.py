from crane.Backend.CommonRegistry import CommonRegistry
from crane.Backend.DockerHub import DockerHub
from crane.Backend.Registry import Registry
from crane.Backend.DockerPrivate import DockerPrivate

import pytest
import json

a_url = "a_url"
username = "a_username"
password = "a_password"
a_json = json.dumps({
    "text": "a",
    "b": "b"
})


@pytest.fixture
def common_registry():
    return CommonRegistry(a_url, username, password)


@pytest.fixture
def dockerhub(url, requests_module):
    return DockerHub(url, username, password, requests_module)


@pytest.fixture
def registry():
    return Registry()


class Response:
    def __init__(self, text):
        self.text = text


class requestsMock:
    def __init__(self, expectations):
        self.expectations = expectations

    def get(self, url, **kwargs):
        return Response(self.expectations[url])


class TestCommonRegistry:
    def test_initialization(self):
        assert(common_registry().url == a_url)
        assert(common_registry().username == username)
        assert(common_registry().password == password)

    def test_search(self):
        with pytest.raises(NotImplementedError):
            common_registry().search("a")

    def test_image(self):
        with pytest.raises(NotImplementedError):
            common_registry().image("a", "b")

    def test_tags(self):
        with pytest.raises(NotImplementedError):
            common_registry().tags("a")

class TestDockerHub:
    def test_query_tags(self):
        requests = requestsMock({"a_url/v1/repositories/a/tags": a_json})
        assert(dockerhub("a_url", requests)._query_tags("a") == json.loads(a_json))

    def test_search_one_page(self):
        result = '{"num_pages": 1, "num_results": 1, "results": [{"is_automated": true, "name": "talien/crane", "is_trusted": true, "is_official": false, "star_count": 0, "description": ""}], "page_size": 25, "query": "talien/crane", "page": "1"}'
        requests = requestsMock({"a_url/v1/search?q=talien/crane&page=1": result})
        expected_output = [{u'is_automated': True, u'name': u'talien/crane', u'star_count': 0, u'is_trusted': True, u'is_official': False, u'description': u''}]
        assert dockerhub("a_url", requests).search("talien/crane") == expected_output


class TestRegistry:
    def test_expand_results_with_registry_name(self):
        results_parameter = [{'a': "a"}, {'b': "b"}]
        class registry_parameter:
            name = "Almafa"
            id = "42"

        expected = [
            {
                'a': "a",
                'registry': "Almafa",
                'registry_id': "42"},
            {
                'b': "b",
                'registry': "Almafa",
                'registry_id': "42"}]

        assert registry()._expand_results_with_registry_name(results_parameter, registry_parameter) == expected

    def test_get_provider(self):
        class registry_parameter_dockerhub:
            provider = "dockerhub"
            url = "a"
            username = "b"
            password = "c"
            requests = None
        class registry_parameter_dockerprivate:
            provider = "private"
            url = "csill"
            username = "am"
            password = "poni"
            requests = None

        assert isinstance(registry()._get_provider(registry_parameter_dockerhub), DockerHub)
        assert registry()._get_provider(registry_parameter_dockerhub).url == "a"
        assert registry()._get_provider(registry_parameter_dockerhub).username == "b"
        assert registry()._get_provider(registry_parameter_dockerhub).password == "c"
        assert isinstance(registry()._get_provider(registry_parameter_dockerprivate), DockerPrivate)
        assert registry()._get_provider(registry_parameter_dockerprivate).url == "csill"
        assert registry()._get_provider(registry_parameter_dockerprivate).username == "am"
        assert registry()._get_provider(registry_parameter_dockerprivate).password == "poni"
