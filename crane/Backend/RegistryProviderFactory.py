from crane.Backend.DockerHub import DockerHub
from crane.Backend.DockerPrivate import DockerPrivate
import requests

class RegistryProviderFactory:
    def create_provider(self, registry):
        if registry.provider == 'dockerhub':
            return DockerHub(registry.url, registry.username, registry.password, requests)
        elif registry.provider == 'private':
            return DockerPrivate(registry.url, registry.username, registry.password, requests)

