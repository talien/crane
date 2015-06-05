from crane.registry import CommonRegistry
from crane.registry import DockerHub

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
        #assert(dockerhub().__query_tags("a") == json.loads(a_json))
        pass
