from crane.webserver import app, db
db.create_all()
app.run(debug=True)
