from crane.hosts import Host

class TestHost:
    def test_repr(self):
        host = Host(1, 'a', 'talien', 'b', 'c')
        assert host.__repr__() == "<User 'talien'>"
