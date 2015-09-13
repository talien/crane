from crane.Backend.Models.HostModel import HostModel

class TestHostModel(object):
    def test_repr(self):
        host = HostModel(1, 'a', 'talien', 'b', 'c')
        assert host.__repr__() == "<User 'talien'>"
