from webserver import db, app
from flask import jsonify, request
import json

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    template = db.Column(db.Text())

    def __init__(self, name, template):
       self.name = name
       self.template = template

@app.route('/template', methods=['POST'])
def new_template():
    data = request.get_json();
    template = Template(data['name'],json.dumps(data['template']));
    db.session.add(template)
    db.session.commit()
    return ""

@app.route('/template', methods=['GET'])
def get_templates():
    templates = Template.query.all()
    result = []
    for template in templates:
        template_json = json.loads(template.template)
        template_json['id'] = template.id
        template_json['name'] = template.name
        result.append(template_json)
    return jsonify(result=result)

@app.route('/template/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    template = Template.query.filter_by(id=template_id).first()
    if template:
       db.session.delete(template)
       db.session.commit()
    return ""
