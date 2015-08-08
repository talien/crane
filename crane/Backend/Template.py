from crane.Backend.Models.TemplateModel import TemplateModel
from crane.webserver import db
import json
from sqlalchemy import desc


class Template:
    def __init__(self):
        pass

    def new_template(self, data):
        last_template_id = self._get_latest_template_id()
        if last_template_id is None:
            last_template_id = 0
        template = TemplateModel(data['name'], json.dumps(data['template']), last_template_id + 1, 0)
        db.session.add(template)
        db.session.commit()
        return template.template_id

    def edit_template(self, template_id, data):
        last_template = TemplateModel.query.filter_by(template_id=template_id, latest=True).first()
        version = last_template.template_version
        last_template.latest = False
        db.session.add(last_template)
        template = TemplateModel(data['name'],json.dumps(data['template']), last_template.template_id, version + 1)
        db.session.add(template)
        db.session.commit()

    def get_templates(self):
        templates = TemplateModel.query.filter_by(latest=True).all()
        result = []
        for template in templates:
            template_json = json.loads(template.template)
            template_json['id'] = template.template_id
            template_json['name'] = template.name
            result.append(template_json)
        return result

    def delete_template(self, template_id):
        templates = TemplateModel.query.filter_by(template_id=template_id).all()
        for template in templates:
            db.session.delete(template)
        db.session.commit()

    def _get_latest_template_id(self):
        templates = TemplateModel.query.order_by(desc("template_id"))
