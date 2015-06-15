from crane.webserver import db


class TemplateModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    template = db.Column(db.Text())
    template_id = db.Column(db.Integer, nullable=False)
    template_version = db.Column(db.Integer, nullable=False)
    latest = db.Column(db.Boolean)

    def __init__(self, name, template, template_id, version):
        self.name = name
        self.template = template
        self.template_id = template_id
        self.template_version = version
        self.latest = True
