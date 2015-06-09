from crane.Backend.Deployer import Deployer
import pytest


@pytest.fixture
def deployer():
    return Deployer()


class TestDeployer:

    def test_generate_parameters(self):
        expected = "-v a -v b -v c "
        assert deployer()._generate_parameters("a b c", "-v") == expected
        expected = ""
        assert deployer()._generate_parameters("", "-v") == expected
