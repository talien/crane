import pytest

from crane.Backend.HostProvider import HostProvider
from crane.Backend.Tests.Mocks import MockSSH
from crane.Backend.Environments import EnvironmentProvider
from crane.webserver import app, db


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'


@pytest.fixture(scope='session', autouse=True)
def clear_db():
    db.drop_all()
    db.create_all()


@pytest.fixture
def environment_provider(host_provider):
    return EnvironmentProvider(host_provider)


class TestEnvironmentProvider(object):
    def test_add_environment(self):
        assert len(environment_provider("").get_environments()) == 0
        environment = environment_provider("").add_environment("an_environment")
        assert len(environment_provider("").get_environments()) == 1
        assert environment_provider("").get_environments()[0]['name'] == "an_environment"
        environment_provider("").delete_environment(environment)

    def test_delete_environment(self):
        assert len(environment_provider("").get_environments()) == 0
        environment = environment_provider("").add_environment("an_environment")
        environment_2 = environment_provider("").add_environment("second_environment")
        assert len(environment_provider("").get_environments()) == 2
        environment_provider("").delete_environment(environment)
        assert len(environment_provider("").get_environments()) == 1
        assert environment_provider("").get_environments()[0]['name'] == "second_environment"
        environment_provider("").delete_environment(environment_2)
        assert len(environment_provider("").get_environments()) == 0

    def test_add_host_to_environment(self):
        host_provider = HostProvider("")
        data = {
            'name': 'Csillamponi',
            'host': 'crane.gov',
            'username': 'Bela',
            'password': 'encrypted'
        }
        host_id = host_provider.add_host(data)
        assert len(environment_provider(host_provider).get_environments()) == 0
        environment_id = environment_provider(host_provider).add_environment("an_environment")
        environment_provider(host_provider).add_host_to_environment(environment_id, host_id)
        the_environment = environment_provider(host_provider).get_environment_by_id(environment_id)
        assert the_environment.name == "an_environment"
        assert len(the_environment.hosts) == 1
        assert the_environment.hosts[0].username == "Bela"
        environment_provider(host_provider).delete_host_from_environment(environment_id, host_id)
        environment_provider(host_provider).delete_environment(environment_id)
        host_provider.delete_host(host_id)
        assert len(environment_provider(host_provider).get_environments()) == 0
