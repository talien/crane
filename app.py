from crane.webserver import app, db
import argparse
import crane.templates
import crane.hosts
import crane.containers
import crane.registry
import crane.environments

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-ip", dest="ip", default="127.0.0.1")
    args = parser.parse_args()
    db.create_all()
    app.run(debug=True, host=args.ip)

main() 
