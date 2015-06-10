from crane.webserver import db
from crane.Backend.DockerHub import DockerHub
from crane.Backend.DockerPrivate import DockerPrivate
import requests


class RegistryModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    url = db.Column(db.String(1024))
    username = db.Column(db.String(256))
    password = db.Column(db.String(1024))
    provider = db.Column(db.String(32))

    def __init__(self, name, url, username, password, provider):
        self.name = name
        self.url = url
        self.username = username
        self.password = password
        self.provider = provider

    def get_provider(self):
        if self.provider == 'dockerhub':
            return DockerHub(self.url, self.username, self.password, requests)
        elif self.provider == 'private':
            return DockerPrivate(self.url, self.username, self.password, requests)