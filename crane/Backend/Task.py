import concurrent.futures
from datetime import datetime
import uuid
import traceback

from crane.Backend.Deployer import Deployer
from crane.Backend.Container import Container
from crane.Backend.Models.TaskModel import TaskModel
from crane.webserver import db

taskrunner = concurrent.futures.ThreadPoolExecutor(max_workers=100)

class Tasks(object):
    def __init__(self, host_provider):
        self.host_provider = host_provider
        self.deployer = Deployer(host_provider)

    def __add_task(self, name, host_id, task_uuid):
        model = TaskModel(name, host_id, task_uuid)
        db.session.add(model)
        db.session.commit()

    def __finish_task(self, task_uuid):
        task = TaskModel.query.filter_by(container_name=task_uuid).first()
        if task.state == "RUNNING":
            task.state = "FINISHED"
            task.finished = datetime.now()
            db.session.add(task)
            db.session.commit()

    def __deploy_task(self, data):
        try:
            task_uuid = str(uuid.uuid4())
            self.__add_task(data['name'], data['host_id'], task_uuid)
            data['container']['name'] = task_uuid
            res = self.deployer.task(data['host_id'], data)
            self.__finish_task(task_uuid)
        except Exception as e:
            f = open("/tmp/exception.log", "w")
            f.write(traceback.format_exc())
            f.close()
            raise

    def create(self, data):
        taskrunner.submit(self.__deploy_task, data)

    def query(self):
        tasks = TaskModel.query.all()
        result = [{'name': task.name,
                   'container_id': task.container_name,
                   'state': task.state,
                   'host': task.host_id,
                   'started': task.started,
                   'finished': task.finished}
                  for task in tasks]
        return result

    def stop(self, id):
        task = TaskModel.query.filter_by(container_name=id).first()
        container = Container(self.host_provider)
        container.stop_container(task.host_id, task.container_name)
        task.state = "STOPPED"
        task.finished = datetime.now()
        db.session.add(task)
        db.session.commit()

    def logs(self, id):
        task = TaskModel.query.filter_by(container_name=id).first()
        container = Container(self.host_provider)
        result = container.get_container_logs(task.host_id, task.container_name, "all")
        return result

    def remove(self, id):
        task = TaskModel.query.filter_by(container_name=id).first()
        container = Container(self.host_provider)
        result = container.remove_container(task.host_id, task.container_name)
        db.session.delete(task)
        db.session.commit()
        return result
