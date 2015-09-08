import requests
import pytest

from crane.Backend.Registry import Registry
from crane.Backend.DockerHub import DockerHub
from crane.Backend.DockerPrivate import DockerPrivate
from crane.Backend.RegistryProviderFactory import RegistryProviderFactory
from crane.webserver import app, db

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'


@pytest.fixture(scope='session', autouse=True)
def clear_db():
    db.drop_all()
    db.create_all()


@pytest.fixture
def registry(providerfactory=RegistryProviderFactory()):
    return Registry(providerfactory)


class TestRegistry(object):
    def test_expand_results_with_registry_name(self):
        results_parameter = [{'a': "a"}, {'b': "b"}]
        class registry_parameter(object):
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
        class registry_parameter_dockerhub(object):
            provider = "dockerhub"
            url = "a"
            username = "b"
            password = "c"
            requests = None
        class registry_parameter_dockerprivate(object):
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

    def test_get_tags(self):
        data = {
            'name': 'csillamponi',
            'url': 'crane.gov',
            'username': '',
            'password': '',
            'provider': 'dockerhub'
        }
        a_registry = registry(MockProviderFactory()).add_registry(data)
        assert registry(MockProviderFactory()).get_tags(a_registry, "", "a_reponame") == "a_reponame_hub_tags"
        assert registry(MockProviderFactory()).get_tags(a_registry, "namespace", "a_reponame") == "namespace/a_reponame_hub_tags"
        registry(MockProviderFactory()).delete_registry(a_registry)
        data['provider'] = 'private'
        b_registry = registry(MockProviderFactory()).add_registry(data)
        assert registry(MockProviderFactory()).get_tags(b_registry, "", "a_reponame") == "a_reponame_private_tags"
        assert registry(MockProviderFactory()).get_tags(b_registry, "namespace", "a_reponame") == "namespace/a_reponame_private_tags"
        registry(MockProviderFactory()).delete_registry(b_registry)

    def test_get_image(self):
        data = {
            'name': 'csillamponi',
            'url': 'crane.gov',
            'username': '',
            'password': '',
            'provider': 'dockerhub'
        }
        a_registry = registry(MockProviderFactory()).add_registry(data)
        assert registry(MockProviderFactory()).get_image(a_registry, "", "a_reponame", "image_id") == "a_reponame_hub_image"
        assert registry(MockProviderFactory()).get_image(a_registry, "namespace", "a_reponame", "image_id") == "namespace/a_reponame_hub_image"
        registry(MockProviderFactory()).delete_registry(a_registry)
        data['provider'] = 'private'
        b_registry = registry(MockProviderFactory()).add_registry(data)
        assert registry(MockProviderFactory()).get_image(b_registry, "", "a_reponame", "image_id") == "a_reponame_private_image"
        assert registry(MockProviderFactory()).get_image(b_registry, "namespace", "a_reponame", "image_id") == "namespace/a_reponame_private_image"
        registry(MockProviderFactory()).delete_registry(b_registry)

    def test_get_registries(self):
        data = {
            'name': 'csillamponi',
            'url': 'crane.gov',
            'username': '',
            'password': '',
            'provider': 'dockerhub'
        }
        registry_ids = [registry().add_registry(data),
                        registry().add_registry(data),
                        registry().add_registry(data)]
        regs = []
        for reg_id in registry_ids:
            data['id'] = reg_id
            regs.append(data.copy())
        assert regs == registry().get_registries()
        for reg_id in registry_ids:
            registry().delete_registry(reg_id)

    def test_search_registry(self):
        data = {
            'name': 'csillamponi',
            'url': 'crane.gov',
            'username': '',
            'password': '',
            'provider': 'dockerhub'
        }
        a_registry = registry(MockProviderFactory()).add_registry(data)
        data['name'] += "2"
        data['provider'] = 'private'
        b_registry = registry(MockProviderFactory()).add_registry(data)
        expected = [
            {'stuff': 'hub_query',
             'registry': 'csillamponi',
             'registry_id': 1},
            {'stuff': 'private_query',
             'registry': 'csillamponi2',
             'registry_id': 2},
        ]
        assert registry(MockProviderFactory()).search_registry("a") == expected
        registry(MockProviderFactory()).delete_registry(a_registry)
        registry(MockProviderFactory()).delete_registry(b_registry)

class MockProviderFactory(object):
    def create_provider(self, registry):
        if registry.provider == 'dockerhub':
            return DockerHubMock(registry.url, registry.username, registry.password, requests)
        elif registry.provider == 'private':
            return DockerPrivateMock(registry.url, registry.username, registry.password, requests)

class DockerHubMock(object):
    def __init__(self, a, b, c, d):
        pass
    def tags(self, a):
        return a+'_hub_tags'
    def image(self, a, b):
        return a+'_hub_image'
    def search(self, a):
        return [{'stuff': 'hub_query'}]


class DockerPrivateMock(object):
    def __init__(self, a, b, c, d):
        pass
    def tags(self, a):
        return a+'_private_tags'
    def image(self, a, b):
        return a+'_private_image'
    def search(self, a):
        return [{'stuff': 'private_query'}]
