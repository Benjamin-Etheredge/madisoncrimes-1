from app import app
from app import scrape

from flask import jsonify, send_from_directory, Response

import os

s = scrape.MadisonScraper()

@app.route('/')
@app.route('/index')
def index():
    return 'Hello World!'

@app.route('/status/sync')
def sync_status():
    status = s.sync_status()
    return status

@app.route('/status/convert')
def convert_status():
    status = s.convert_status()
    return status

@app.route('/arrest/report')
def arrest_reports():
    return {'reports': s.arrests()}

@app.route('/arrest/report/<report>')
def arrest_report(report):
    arrests = []
    ta = s.arrest(report)
    ta_clean = scrape.clean_report(ta)
    for record in scrape.extract_arrests(ta_clean, report):
        arrests.append(record)
    return {'arrests': arrests}

@app.route('/incident/report')
def incident_reports():
    return {'reports': s.incidents()}

@app.route('/incident/report/<report>')
def incident_report(report):
    incidents = []
    ti = s.incident(report)
    ti_clean = scrape.clean_report(ti)
    ti_ref = scrape.reformat_incident(ti_clean)
    for record in scrape.extract_records(ti_ref, report):
        incidents.append(record)
    return {'incidents': incidents}

@app.route('/incident/report/<report>/text')
def incident_report_raw(report):
    return Response(s.incident(report), mimetype='text/plain')

@app.route('/incident/report/<report>/pdf')
def incident_report_pdf(report):
    return Response(s.incident_pdf(report), mimetype='application/pdf')

