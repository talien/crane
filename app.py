from crane.webserver import app, db
from crane.config import config
import crane.index
import crane.templates
import crane.hosts
import crane.containers
import crane.registry
import crane.environments
import crane.task


def main():
    db.create_all()
    app.run(debug=config['general']['debug'], host=config['network']['listen_ip'], port=config['network']['port'])

main()
