from app import app, db
from app.models import ArrestReport, IncidentReport, Location, Incident

@app.shell_context_processor
def make_shell_context():
    return {
                'db': db,
                'ArrestReport': ArrestReport,
                'IncidentReport': IncidentReport,
                'Location': Location,
                'Incident': Incident
            }
