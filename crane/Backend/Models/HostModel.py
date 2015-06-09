from crane.webserver import db
import datetime


class HostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    host = db.Column(db.String(1024))
    username = db.Column(db.String(256))
    password = db.Column(db.String(1024))
    sshkey = db.Column(db.Text())

    def __init__(self, name, host, username, password, sshkey):
        self.name = name
        self.host = host
        self.username = username
        self.password = password
        self.sshkey = sshkey

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        cls = self.__class__
        convert = { "DATETIME": datetime.datetime.isoformat}
        result = {}
        for column in cls.__table__.columns:
            column_name = getattr(self, column.name)
            current_type = str(column.type)
            if current_type in convert.keys() and column_name is not None:
                try:
                    result[column.name] = convert[current_type](column_name)
                except:
                    result[column.name] = "Error:  Failed to covert using ", unicode(convert[current_type])
            elif column_name is None:
                result[column.name] = unicode()
            else:
                result[column.name] = column_name
        return result
