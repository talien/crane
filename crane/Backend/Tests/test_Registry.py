from crane.Backend.Registry import Registry
from crane.Backend.DockerHub import DockerHub
from crane.Backend.DockerPrivate import DockerPrivate
from crane.webserver import db
import pytest

db.create_all()


@pytest.fixture
def registry():
    return Registry()


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

    def test_add_registry(self):
        data = {
            'name': 'csillamponi',
            'url': 'crane.gov',
            'username': '',
            'password': '',
            'provider': 'dockerhub'
        }
        the_id = registry().add_registry(data)
        inserted_registry = registry().get_registry_by_id(the_id)
        assert inserted_registry.name == 'csillamponi'
        assert inserted_registry.url == 'crane.gov'
        assert inserted_registry.username == ''
        assert inserted_registry.password == ''
        assert inserted_registry.provider == 'dockerhub'
        registry().delete_registry(the_id)

    def test_update_registry(self):
        data_before_update = {
            'name': 'csillamponi',
            'url': 'crane.gov',
            'username': '',
            'password': '',
            'provider': 'dockerhub'
        }
        data_after_update = {
            'name': 'csillamponi2',
            'url': 'crane.gov2',
            'username': '2',
            'password': '2',
            'provider': 'dockerhub2'
        }
        the_id = registry().add_registry(data_before_update)
        registry().update_registry(the_id, data_after_update)
        updated_record = registry().get_registry_by_id(the_id)
        assert updated_record.name == 'csillamponi2'
        assert updated_record.url == 'crane.gov2'
        assert updated_record.username == '2'
        assert updated_record.password == '2'
        assert updated_record.provider == 'dockerhub2'
        registry().delete_registry(the_id)

    def test_delete_registry(self):
        data = {
            'name': 'csillamponi',
            'url': 'crane.gov',
            'username': '',
            'password': '',
            'provider': 'dockerhub'
        }
        the_id = registry().add_registry(data)
        assert registry().get_registry_by_id(the_id) is not None
        registry().delete_registry(the_id)
        assert registry().get_registry_by_id(the_id) is None
