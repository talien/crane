from crane.hosts import HostModel

class TestHost:
    def test_repr(self):
        host = HostModel(1, 'a', 'talien', 'b', 'c')
        assert host.__repr__() == "<User 'talien'>"
