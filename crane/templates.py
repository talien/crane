from webserver import db, app
from flask import jsonify, request
from sqlalchemy import desc
import json

class Template(db.Model):
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

    @staticmethod
    def get_latest_template_id():
        templates = Template.query.order_by(desc("template_id"))

@app.route('/template', methods=['POST'])
def new_template():
    data = request.get_json();
    last_template_id = Template.get_latest_template_id()
    if last_template_id == None:
        last_template_id = 0
    template = Template(data['name'],json.dumps(data['template']), last_template_id + 1, 0);
    db.session.add(template)
    db.session.commit()
    return ""

@app.route('/template/<template_id>', methods=['POST'])
def edit_template(template_id):
    data = request.get_json();
    last_template = Template.query.filter_by(template_id=template_id, latest=True).first()
    version = last_template.template_version
    last_template.latest = False
    db.session.add(last_template)
    template = Template(data['name'],json.dumps(data['template']), last_template.template_id, version + 1);
    db.session.add(template)
    db.session.commit()
    return ""

@app.route('/template', methods=['GET'])
def get_templates():

    templates = Template.query.filter_by(latest=True).all()
    result = []
    for template in templates:
        template_json = json.loads(template.template)
        template_json['id'] = template.template_id
        template_json['name'] = template.name
        result.append(template_json)
    return jsonify(result=result)

@app.route('/template/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    templates = Template.query.filter_by(template_id=template_id).all()
    for template in templates:
       db.session.delete(template)
    db.session.commit()
    return ""
