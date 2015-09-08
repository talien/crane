import pytest
import json

from crane.Backend.DockerPrivate import DockerPrivate
from crane.Backend.Tests.Mocks import requestsMock

username = "a_username"
password = "a_password"
a_json = json.dumps({
    "text": "a",
    "b": "b"
})

@pytest.fixture
def dockerprivate(url, the_username, requests_module):
    return DockerPrivate(url, the_username, password, requests_module)


class TestDockerPrivate:
    def test_search_with_username(self):
        requests = requestsMock({"a_url/v1/search?q=talien/crane": {'response': '{"results": "the_results", "b": "a"}',
                                                                    'headers': 'a'}})
        expected_results = "the_results"
        assert dockerprivate("a_url", username, requests).search("talien/crane") == expected_results

    def test_search_without_username(self):
        requests = requestsMock({"a_url/v1/search?q=talien/crane": {'response': '{"results": "the_results", "b": "a"}',
                                                                    'headers': 'a'}})
        expected_results = "the_results"
        assert dockerprivate("a_url", "", requests).search("talien/crane") == expected_results

    def test_tags(self):
        tags = '{"k1": "v1", "k2": "v2", "k3": "v1"}'
        requests = requestsMock({"a_url/v1/repositories/talien/crane/tags": {'response': tags,
                                                                             'headers': 'a'}})
        expected_results = [{'name': 'v1', 'tags': ['k3', 'k1']}, {'name': 'v2', 'tags': ['k2']}]
        assert dockerprivate("a_url", username, requests).tags("talien/crane") == expected_results

    def test_images(self):
        ancestors = '["a123", "2"]'
        requests = requestsMock({"a_url/v1/images/a123/ancestry": {'response': ancestors,
                                                                   'headers': 'a'},
                                 "a_url/v1/images/a123/json": {'response': '{"res1": "1"}',
                                                               'headers': 'a'},
                                 "a_url/v1/images/2/json": {'response': '{"res2": "2"}',
                                                            'headers': 'a'}})

        expected_results = [{'res1': '1'}, {'res2': '2'}]
        assert dockerprivate("a_url", username, requests).image("talien/crane", "a123") == expected_results
