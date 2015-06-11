from crane.Backend.CommonRegistry import CommonRegistry
from crane.Backend.DockerHub import DockerHub
from crane.Backend.Registry import Registry
from crane.Backend.DockerPrivate import DockerPrivate

import pytest
import json

url = "a_url"
username = "a_username"
password = "a_password"
a_json = json.dumps({
    "text": "a",
    "b": "b"
})


@pytest.fixture
def common_registry():
    return CommonRegistry(url, username, password)


@pytest.fixture
def dockerhub():
    return DockerHub(url, username, password, requests)


@pytest.fixture
def registry():
    return Registry()


class Response:
    def __init__(self, text):
        self.text = text


class requests:
    @staticmethod
    def get(url, **kwargs):
        return Response(a_json)


class TestCommonRegistry:
    def test_initialization(self):
        assert(common_registry().url == url)
        assert(common_registry().username == username)
        assert(common_registry().password == password)


class TestDockerHub:
    def test_query_tags(self):
        assert(dockerhub()._query_tags("a") == json.loads(a_json))


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
