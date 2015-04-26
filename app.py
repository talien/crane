from crane.webserver import app, db
import argparse

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--listen-ip", dest="ip", default="127.0.0.1")
  args = parser.parse_args()
  db.create_all()
  app.run(debug=True, host=args.ip)

main() 
