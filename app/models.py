from app import db

inc_association_table = db.Table('incident_to_incident_report',
                                 db.Model.metadata,
                         db.Column('incident_report_id', db.Integer, db.ForeignKey('incident_report.id')),
                         db.Column('incident_id', db.Integer, db.ForeignKey('incident.id'))
)

arr_association_table = db.Table('incident_to_arrest_report', db.Model.metadata,
                         db.Column('arrest_report_id', db.Integer, db.ForeignKey('arrest_report.id')),
                         db.Column('incident_id', db.Integer, db.ForeignKey('incident.id'))
)

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(250), nullable=False, unique=True)
    needs_moderation = db.Column(db.Boolean, nullable=False, default=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(500))
    raw = db.Column(db.String(10000))

    def __repr__(self):
        return '<Location: id=%d location=%s>' % (self.id, self.location)


class Incident(db.Model):
    __tablename__ = 'incident'
    id = db.Column(db.Integer, primary_key=True)
    incident = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return '<Incident: id=%d incident=%s>' % (self.id, self.incident)

class IncidentReport(db.Model):
    __tablename__ = 'incident_report'
    id = db.Column(db.Integer, primary_key=True)
    shift = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    case = db.Column(db.String(25), nullable=False, unique=True)
    report_num = db.Column(db.Integer, nullable=False)

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship(Location)
    incidents = db.relationship('Incident', secondary=inc_association_table)

class ArrestReport(db.Model):
    __tablename__ = 'arrest_report'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    case = db.Column(db.String(25), nullable=False, unique=True)
    person = db.Column(db.String(255), nullable=False)
    person_res = db.Column(db.String(255), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship(Location)
    incidents = db.relationship("Incident", secondary=arr_association_table)
