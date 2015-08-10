from crane.Backend.Template import Template
from crane.webserver import db
import pytest
import json

db.drop_all()
db.create_all()

@pytest.fixture
def template():
    return Template()


class TestTemplate:
    def test_new_template(self):
        data = {
            'name': 'a_template',
            'template': {
                'a': 'b',
                'c': 'd'
            }
        }
        template_id = template().new_template(data)
        a_template = template().get_template_by_id(template_id)
        assert a_template.name == 'a_template'
        assert json.loads(a_template.template)['a'] == 'b'
        assert json.loads(a_template.template)['c'] == 'd'
        template().delete_template(template_id)

    def test_delete_template(self):
        data = {
            'name': 'a_template',
            'template': {
                'a': 'b',
                'c': 'd'
            }
        }
        the_id = template().new_template(data)
        assert template().get_template_by_id(the_id) is not None
        template().delete_template(the_id)
        assert template().get_template_by_id(the_id) is None

    def test_update_template(self):
        data = {
            'name': 'a_template',
            'template': {
                'a': 'b',
                'c': 'd'
            }
        }
        template_id = template().new_template(data)
        a_template = template().get_template_by_id(template_id)
        assert a_template.name == 'a_template'
        assert json.loads(a_template.template)['a'] == 'b'
        assert json.loads(a_template.template)['c'] == 'd'
        data2 = {
            'name': 'a_template',
            'template': {
                'f': 'g',
                'c': 'd'
            }
        }
        template().edit_template(template_id, data2)
        a_template = template().get_template_by_id(template_id)
        assert a_template.name == 'a_template'
        print json.loads(a_template.template)
        assert json.loads(a_template.template)['f'] == 'g'
        assert json.loads(a_template.template)['c'] == 'd'
        template().delete_template(template_id)

    def test_get_templates(self):
        data = {
            'name': 'a_template',
            'template': {
                'a': 'b',
                'c': 'd'
            }
        }
        data2 = {
            'name': 'b_template',
            'template': {
                'f': 'g',
                'h': 'j'
            }
        }
        template_id = template().new_template(data)
        template_id_2 = template().new_template(data2)

        expected = [
            {
                'a': 'b',
                'c': 'd',
                'id': template_id,
                'name': 'a_template'},
            {
                'f': 'g',
                'h': 'j',
                'id': template_id_2,
                'name': 'b_template'
            }

        ]
        assert template().get_templates() == expected
        template().delete_template(template_id)
        template().delete_template(template_id_2)
