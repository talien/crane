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
    def __init__(self, text, headers):
        self.text = text
        self.headers = headers


class requestsMock:
    def __init__(self, expectations):
        self.expectations = expectations

    def get(self, url, **kwargs):
        return Response(self.expectations[url]['response'], self.expectations[url]['headers'])


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
        requests = requestsMock({"a_url/v1/repositories/a/tags": {'response': a_json, 'headers': "a"}})
        assert(dockerhub("a_url", requests)._query_tags("a") == json.loads(a_json))

    def test_search_one_page(self):
        result = '{"num_pages": 1, "num_results": 1, "results": [{"is_automated": true, "name": "talien/crane", "is_trusted": true, "is_official": false, "star_count": 0, "description": ""}], "page_size": 25, "query": "talien/crane", "page": "1"}'
        requests = requestsMock({"a_url/v1/search?q=talien/crane&page=1": {'response': result, 'headers': "a"}})
        expected_output = [{u'is_automated': True, u'name': u'talien/crane', u'star_count': 0, u'is_trusted': True, u'is_official': False, u'description': u''}]
        assert dockerhub("a_url", requests).search("talien/crane") == expected_output

    def test_search_multiple_pages(self):
        result1 = '{"num_pages": 2, "num_results": 1, "results": [{"is_automated": true, "name": "talien/crane", "is_trusted": true, "is_official": false, "star_count": 0, "description": ""}], "page_size": 25, "query": "talien/crane", "page": "1"}'
        result2 = '{"num_pages": 2, "num_results": 1, "results": [{"is_automated": false, "name": "laci/crane", "is_trusted": true, "is_official": false, "star_count": 0, "description": ""}], "page_size": 25, "query": "talien/crane", "page": "2"}'
        requests = requestsMock({"a_url/v1/search?q=talien/crane&page=1": {'response': result1, 'headers': "a"},
                                 "a_url/v1/search?q=talien/crane&page=2": {'response': result2, 'headers': "a"}})
        expected_output = [{u'is_automated': True, u'name': u'talien/crane', u'star_count': 0, u'is_trusted': True, u'is_official': False, u'description': u''}, {u'is_automated': False, u'name': u'laci/crane', u'star_count': 0, u'is_trusted': True, u'is_official': False, u'description': u''}]
        assert dockerhub("a_url", requests).search("talien/crane") == expected_output

    def test_tags(self):
        tags = '[{"layer": "8bdc8703", "name": "build"}]'
        images = '[{"checksum": "", "id": "8bdc8703a0096252bdf97dfc151667062b9e7c2098884247e8fce97ea1824d67"}, {"checksum": "", "id": "f088b8ddbfde7da26520d9fa7c8eecc3cd31e70878cb96c86e29fdb36ba70fbd"}, {"checksum": "", "id": "50faae8ad7b73c842f4ab96e6d992c8b47c4797cf5b752b9055bf25db1189921"}, {"checksum": "", "id": "80c6b693531eaea4b09e1893fc1148c33fc120ce5510e574ff3d96efea1c192d"}, {"checksum": "", "id": "3f0a76880821ecb8b007957137b045dedc9600167b9f7dc0c9ca8b5f455a9d65"}, {"checksum": "", "id": "dc9883fddd550033b7615f6772514add1ae8f26d01f2e24f165a290a33c58a35"}, {"checksum": "", "id": "9cbaf023786cd79dfba46f49d9a04b2fe9f18017db1257094d1d4cbe7ccb00f1"}, {"checksum": "", "id": "03db2b23cf0332af20d600e1e0306a629235f4d3b2cfcab2cad0bc3d3443b2b7"}, {"checksum": "", "id": "8f321fc43180b5f59e6e3da297084e1b0af43ce7b80a019554f84e66c2a33ebe"}, {"checksum": "", "id": "6a459d727ebbbe9802ccd10f865e47f1cfcb37e6f80f3af06ad51c426e912c12"}, {"checksum": "", "id": "2dcbbf65536cc878b5d437a7083fb255dd3e00d2cac2e78c9484ad466dced149"}, {"checksum": "", "id": "97fd97495e494f13f514b5911ec9587b7c91914b01754b9ecb6f165820860ac4"}, {"checksum": "", "id": "511136ea3c5a64f264b78b5433614aec563103b4d4702f3ba7d4d2698e22c158"}, {"checksum": "", "id": "29dce9f32188954611dccfcd7e92cef1f2a874626601a42516685902b5479d21"}, {"checksum": "", "id": "72da3da2d9adeab6f1fb3710806e9d0618ed727413326fd0a071aa54c96146af"}, {"checksum": "", "id": "196cbe903edb76f19dcbfdbb4e5665674b49b1c14f6d00dac717d6b7a6ae7204"}, {"checksum": "", "id": "07a27389aebf3a12457a5c3b81e8780551b9dda41ed0769395e633e83a81f6aa"}, {"checksum": "", "id": "6470287e6c368a685cf864bd420b58003fc0304cf6d7bf9a98180c306c6c8a1a"}, {"checksum": "", "id": "884f522731580b4d64b60c9435211267c19717b4df6b4b77a9b15dc117a186ac"}, {"checksum": "", "id": "8dbd9e392a964056420e5d58ca5cc376ef18e2de93b5cc90e868a1bbc8318c1c"}]'
        requests = requestsMock({"a_url/v1/repositories/balabit/syslog-ng/tags": {'response': tags, 'headers': "a"},
                                 "a_url/v1/repositories/balabit/syslog-ng/images": {'response': images,
                                                                                    'headers': {'x-docker-token': "a",
                                                                                                'x-docker-endpoints': "b"}}})
        expected_result = [{'name': u'8bdc8703a0096252bdf97dfc151667062b9e7c2098884247e8fce97ea1824d67', 'tags': [u'build']}]
        assert dockerhub("a_url", requests).tags("balabit/syslog-ng") == expected_result

    def test_images(self):
        images = '[{"checksum": "", "id": "123"}]'
        ancestry = '["123", "456", "789"]'
        detail1 = '{"comment": "csillam", "created": "today", "id": "123"}'
        detail2 = '{"comment": "csillam2", "created": "today2", "id": "456"}'
        detail3 = '{"comment": "csillam3", "created": "today3", "id": "789"}'
        requests = requestsMock({"a_url/v1/repositories/balabit/syslog-ng/images": {'response': images,
                                                                                    'headers': {'x-docker-token': "dtoken",
                                                                                                'x-docker-endpoints': "dendpoint"}},
                                 "https://dendpoint/v1/images/123/ancestry": {'response': ancestry,
                                                                              'headers': {'x-docker-token': "dtoken",
                                                                                          'x-docker-endpoints': "dendpoint"}},
                                 "https://dendpoint/v1/images/123/json": {'response': detail1,
                                                                          'headers': {'x-docker-token': "dtoken",
                                                                                          'x-docker-endpoints': "dendpoint"}},
                                 "https://dendpoint/v1/images/456/json": {'response': detail2,
                                                                          'headers': {'x-docker-token': "dtoken",
                                                                                          'x-docker-endpoints': "dendpoint"}},
                                 "https://dendpoint/v1/images/789/json": {'response': detail3,
                                                                          'headers': {'x-docker-token': "dtoken",
                                                                                          'x-docker-endpoints': "dendpoint"}}})

        expected_result = [{'comment': 'csillam', 'created': 'today', 'id': '123'}, {'comment': 'csillam2', 'created': 'today2', 'id': '456'}, {'comment': 'csillam3', 'created': 'today3', 'id': '789'}]
        assert dockerhub("a_url", requests).image("balabit/syslog-ng", "123") == expected_result

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
