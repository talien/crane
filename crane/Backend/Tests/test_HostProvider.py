import pytest
from crane.Backend.HostProvider import HostProvider
from crane.Backend.Tests.Mocks import MockSSH


@pytest.fixture
def host_provider(mockssh):
    return HostProvider(mockssh)


class TestHostProvider:
    def test_run_command_on_host(self):
        sshmock = MockSSH([{'type': 'execute',
                            'command': 'docker almafa',
                            'result': {'stdout': 'kortefa', 'stderr': '', 'exit_code': 0}}])
        result = host_provider(sshmock).run_command_on_host("a_host", "docker almafa")
        assert result == {'stdout': 'kortefa', 'stderr': '', 'exit_code': 0}
