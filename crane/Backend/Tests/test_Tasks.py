import pytest

from crane.Backend.HostProvider import HostProvider
from crane.Backend.Tests.Mocks import MockSSH, MockTaskRunner, MockUuid
from crane.Backend.Task import Tasks
from crane.webserver import app, db


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'


def ignore_keys(d, *args):
    d = dict(d)
    for k in args:
        del d[k]
    return d


def ignore_keys_in_list_of_dicts(ld, *args):
    return [ignore_keys(d, *args) for d in ld]


@pytest.fixture(scope='session', autouse=True)
def clear_db():
    db.drop_all()
    db.create_all()


@pytest.fixture
def tasks(host_provider, task_runner, uuid):
    return Tasks(host_provider, task_runner, uuid)


class TestTasks(object):

    def create_task_object(self, taskname):
        return {
            "name": taskname,
            "deploy": "raw",
            "host_id": "0",
            "container": {
                "name": "alma",
                "image": "ubuntu",
                "command": "echo Hello"
            }
        }

    def test_add_task(self):
        runner = MockTaskRunner()
        uuid = MockUuid()
        ssh_mock = MockSSH([{'type': 'execute',
                             'command': 'docker run  --name alma       ubuntu echo Hello',
                             'result': {'stdout': 'korte\n', 'stderr': '', 'exit_code': 0}}])
        host_provider = HostProvider(ssh_mock)
        assert len(tasks(host_provider, runner, uuid).query()) == 0
        task = self.create_task_object("task1")
        tasks(host_provider, runner, uuid).create(task)
        runner.run()
        assert len(tasks(host_provider, runner, uuid).query()) == 1
        assert ignore_keys_in_list_of_dicts(tasks(host_provider, runner, uuid).query(), "started", "finished") == [
            {'container_id': 'alma', 'host': '0', 'name': 'task1', 'state': 'FINISHED'}]

    def test_stop_task(self):
        clear_db()
        runner = MockTaskRunner()
        uuid = MockUuid()
        ssh_mock = MockSSH([{'type': 'execute',
                             'command': 'docker run  --name alma       ubuntu echo Hello',
                             'result': {'stdout': 'korte\n', 'stderr': '', 'exit_code': 0}}])
        host_provider = HostProvider(ssh_mock)
        task = self.create_task_object("task1")
        tasks(host_provider, runner, uuid).create(task)

        def check_function():
            assert ignore_keys_in_list_of_dicts(tasks(host_provider, runner, uuid).query(), 'started', 'finished') == [
                {'container_id': 'alma', 'host': '0', 'name': 'task1', 'state': 'RUNNING'}]
            tasks(host_provider, runner, uuid).stop('alma')
            assert ignore_keys_in_list_of_dicts(tasks(host_provider, runner, uuid).query(), 'started', 'finished') == [
                {'container_id': 'alma', 'host': '0', 'name': 'task1', 'state': 'STOPPED'}]

        ssh_mock.expectations.append({'type': 'after_execute',
                                      'function': check_function})
        ssh_mock.expectations.append({'type': 'execute',
                                      'command': 'docker stop alma',
                                      'result': ''})
        runner.run()

    def test_remove_task(self):
        clear_db()
        runner = MockTaskRunner()
        uuid = MockUuid(['alma', 'korte'])
        ssh_mock = MockSSH([{'type': 'execute',
                             'command': 'docker run  --name alma       ubuntu echo Hello',
                             'result': {'stdout': 'barack\n', 'stderr': '', 'exit_code': 0}},
                            {'type': 'execute',
                             'command': 'docker run  --name korte       ubuntu echo Hello',
                             'result': {'stdout': 'barack\n', 'stderr': '', 'exit_code': 0}},
                            {'type': 'execute',
                             'command': 'docker rm alma',
                             'result': {'stdout': 'barack\n', 'stderr': '', 'exit_code': 0}}
                            ])
        host_provider = HostProvider(ssh_mock)
        assert len(tasks(host_provider, runner, uuid).query()) == 0
        task = self.create_task_object("task1")
        tasks(host_provider, runner, uuid).create(task)
        runner.run()
        task = self.create_task_object("task2")
        tasks(host_provider, runner, uuid).create(task)
        runner.run()
        tasks(host_provider, runner, uuid).remove('alma')
        assert ignore_keys_in_list_of_dicts(tasks(host_provider, runner, uuid).query(), "started", "finished") == [
            {'container_id': 'korte', 'host': '0', 'name': 'task2', 'state': 'FINISHED'}]

    def test_task_logs(self):
        clear_db()
        runner = MockTaskRunner()
        uuid = MockUuid()
        ssh_mock = MockSSH([{'type': 'execute',
                             'command': 'docker run  --name alma       ubuntu echo Hello',
                             'result': {'stdout': 'korte\n', 'stderr': '', 'exit_code': 0}},
                            {'type': 'execute',
                             'command': 'docker logs --tail=all alma',
                             'result': {'stdout': 'korte\n', 'stderr': '', 'exit_code': 0}}
                            ])
        host_provider = HostProvider(ssh_mock)
        assert len(tasks(host_provider, runner, uuid).query()) == 0
        task = self.create_task_object("task1")
        tasks(host_provider, runner, uuid).create(task)
        runner.run()
        assert len(tasks(host_provider, runner, uuid).query()) == 1
        assert ignore_keys_in_list_of_dicts(tasks(host_provider, runner, uuid).query(), "started", "finished") == [
            {'container_id': 'alma', 'host': '0', 'name': 'task1', 'state': 'FINISHED'}]
        assert tasks(host_provider, runner, uuid).logs('alma') == "korte\n"
