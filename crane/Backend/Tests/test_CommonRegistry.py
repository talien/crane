import pytest

from crane.Backend.CommonRegistry import CommonRegistry

a_url = "a_url"
username = "a_username"
password = "a_password"


@pytest.fixture
def common_registry():
    return CommonRegistry(a_url, username, password)


class TestCommonRegistry(object):
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
