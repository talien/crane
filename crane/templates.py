from webserver import app
from flask import jsonify, request
from crane.Backend.Template import Template


templates = Template()


@app.route('/template', methods=['POST'])
def new_template():
    templates.new_template(request.get_json())
    return ""

@app.route('/template/<template_id>', methods=['POST'])
def edit_template(template_id):
    templates.edit_template(template_id, request.get_json())
    return ""

@app.route('/template', methods=['GET'])
def get_templates():
    return jsonify(result=templates.get_templates())

@app.route('/template/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    templates.delete_template(template_id)
    return ""
