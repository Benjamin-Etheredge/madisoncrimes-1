#!/usr/bin/env python

import os
import re
import subprocess

import pandas as pd

from lxml import html
import requests

MADISON_URL = 'https://www.madisonal.gov/Archive.aspx'
INCIDENT_AMID = 67
ARREST_AMID = 68

class MadisonScraper(object):
    def __init__(self, base_path='madisoncrimes-data'):
        self.base_url = MADISON_URL
        self.base_path = base_path
        self.incident_path = os.path.join(self.base_path, 'incidents')
        self.incident_txt_path = os.path.join(self.base_path, 'incidents_txt')
        self.arrest_path = os.path.join(self.base_path, 'arrests')
        self.arrest_txt_path = os.path.join(self.base_path, 'arrests_txt')

        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
        if not os.path.exists(self.incident_path):
            os.mkdir(self.incident_path)
        if not os.path.exists(self.incident_txt_path):
            os.mkdir(self.incident_txt_path)
        if not os.path.exists(self.arrest_path):
            os.mkdir(self.arrest_path)
        if not os.path.exists(self.arrest_txt_path):
            os.mkdir(self.arrest_txt_path)

    def list_reports(self, amid):
        payload = {'AMID': amid, 'Type': '', 'ADID': ''}
        page = requests.get(self.base_url, params=payload)
        tree = html.fromstring(page.text)
        urls = tree.xpath('//span[@class="archive"]/a')
        ret = []
        for url in urls:
            url_s = url.attrib['href']
            url_s = url_s.split('=')
            if len(url_s) < 2:
                continue
            ret.append(url_s[1])
        return ret

    def download_report(self, report_num, path):
        payload = {'ADID': report_num}
        page = requests.get(MADISON_URL, params=payload)
        fname = os.path.join(path, report_num)
        with open(fname, 'wb') as f:
            f.write(page.content)

    def incidents(self):
        return os.listdir(self.incident_path)

    def arrests(self):
        return os.listdir(self.arrest_path)

    def incident_txt(self):
        return os.listdir(self.incident_txt_path)

    def arrest_txt(self):
        return os.listdir(self.arrest_txt_path)

    def online_incidents(self):
        return self.list_reports(INCIDENT_AMID)

    def online_arrests(self):
        return self.list_reports(ARREST_AMID)

    def download_incident(self, report_num):
        self.download_report(report_num, self.incident_path)

    def download_arrest(self, report_num):
        self.download_report(report_num, self.arrest_path)

    def sync_status(self):
        incidents = set(self.incidents())
        online_incidents = set(self.online_incidents())
        new_incidents = online_incidents.difference(incidents)
        removed_incidents = incidents.difference(online_incidents)

        arrests = set(self.arrests())
        online_arrests = set(self.online_arrests())
        new_arrests = online_arrests.difference(arrests)
        removed_arrests = arrests.difference(online_arrests)

        status = {
            'incidents':
                {
                    'cached': len(incidents),
                    'online': len(online_incidents),
                    'removed': len(removed_incidents),
                    'needs_sync': len(new_incidents),
                },
            'arrests':
                {
                    'cached': len(arrests),
                    'online': len(online_arrests),
                    'removed': len(removed_arrests),
                    'needs_sync': len(new_arrests),
                }
            }
        return status

    def sync(self):
        incidents = set(self.incidents())
        online_incidents = set(self.online_incidents())
        new_incidents = online_incidents.difference(incidents)

        for f in new_incidents:
            self.download_incident(f)

        arrests = set(self.arrests())
        online_arrests = set(self.online_arrests())
        new_arrests = online_arrests.difference(arrests)

        for f in new_arrests:
            self.download_arrest(f)

    def convert_status(self):
        incidents = set(self.incidents())
        incident_txt = set(self.incident_txt())
        new_incidents = incidents.difference(incident_txt)

        arrests = set(self.arrests())
        arrest_txt = set(self.arrest_txt())
        new_arrests = arrests.difference(arrest_txt)

        return {
            'incidents':
                {
                    'cached': len(incident_txt),
                    'new': len(new_incidents),
                },
            'arrests':
                {
                    'cached': len(arrest_txt),
                    'new': len(new_arrests),
                }
            }

    def convert(self):
        incidents = set(self.incidents())
        incident_txt = set(self.incident_txt())
        new_incidents = incidents.difference(incident_txt)

        arrests = set(self.arrests())
        arrest_txt = set(self.arrest_txt())
        new_arrests = arrests.difference(arrest_txt)

        for incident in new_incidents:
            self.convert_incident(incident)

        for arrest in new_arrests:
            self.convert_arrest(arrest)

    def convert_incident(self, report_num):
        txt = subprocess.check_output(
                ['pdftotext',
                 '-nopgbrk',
                 '-layout',
                 os.path.join(self.incident_path, report_num),
                 '-'])
        with open(os.path.join(self.incident_txt_path, report_num), 'wb') as f:
            f.write(txt)

    def convert_arrest(self, report_num):
        txt = subprocess.check_output(
                ['pdftotext',
                 '-nopgbrk',
                 os.path.join(self.arrest_path, report_num),
                 '-'])
        with open(os.path.join(self.arrest_txt_path, report_num), 'wb') as f:
            f.write(txt)

    def incident(self, report_num):
        path = os.path.join(self.incident_txt_path, report_num)
        if not os.path.exists(path):
            self.convert_incident(report_num)
        with open(path, 'r') as f:
            lines = f.readlines()
        return lines

    def incident_pdf(self, report_num):
        path = os.path.join(self.incident_path, report_num)
        with open(path, 'rb') as f:
            content = f.read()
        return content


    def arrest(self, report_num):
        path = os.path.join(self.arrest_txt_path, report_num)
        if not os.path.exists(path):
            self.convert_arrest(report_num)
        with open(path, 'r') as f:
            lines = f.readlines()
        return lines


def convert_to_text(file):
    return subprocess.check_output(["pdftotext", "-nopgbrk", "-layout",
                ('pdfs/' + file), '-']).split('\n')

def clean_report(lines):
    keep = []
    rej = ['', '\n', 'Incident Report', 'Arrest Report', 'Madison Police Department', 'Date', 'Arrest Information', 'Arrest', 'Report Designed by the Law Enforcement Technology Coordinator']
    for line in lines:
        line = line.strip()
        if line in rej:
            continue
        if re.match(r'Page \d* of \d*', line):
            continue
        if re.match(r'\((.*) To (.*)\)', line):
            continue
        keep.append(line)
    return keep

def reformat_incident(lines):
    new_lines = []
    for line in lines:
        if line.find('Time:') > 0:
            new_lines.append(line[0:line.find('Time:')])
            line = line[line.find('Time:'):]
        if line.find('Shift:') > 0:
            new_lines.append(line[0:line.find('Shift:')])
            line = line[line.find('Shift:'):]
        if line.find('Location:') > 0:
            new_lines.append(line[0:line.find('Location:')])
            line = line[line.find('Location:'):]
        new_lines.append(line)
    new_lines = [l.strip() for l in new_lines if len(l)]
    return new_lines

def clean_incident(inc):
    inc = inc.replace('-', ' ')
    inc = inc.replace('    ', ' ')
    inc = inc.replace('   ', ' ')
    inc = inc.replace('  ', ' ')
    inc = inc.replace('1st', '1')
    inc = inc.replace('1ST', '1')
    inc = inc.replace('2nd', '2')
    inc = inc.replace('2ND', '2')
    inc = inc.replace('3rd', '3')
    inc = inc.replace('3RD', '3')
    inc = inc.replace('4th', '4')
    inc = inc.replace('4TH', '4')
    inc = inc.strip('.')
    return inc

def extract_arrests(lines, file=None):
    records = []
    record = None

    date_lines = {}
    cno_lines = {}
    other_lines = {}

    for ii, line in enumerate(lines):
        date_match = re.match(r'(\d*)/(\d*)/(\d*)', line)
        case_match = re.match(r'(\d\d)-(\d*)', line)

        if date_match:
            date_lines[ii] = line
        elif case_match:
            cno_lines[ii] = line
        else:
            other_lines[ii] = line

    date_keys = sorted(date_lines.keys())
    cno_keys = sorted(cno_lines.keys())
    other_keys = sorted(other_lines.keys())

    for ii in range(0, len(date_keys) - 1):
        dk = date_keys[ii]
        dkn = date_keys[ii+1]
        ck = [ ck for ck in cno_keys if ck > dk and ck < dkn][0]
        between_dk_ck = [ok for ok in other_keys if ok > dk and ok < ck]
        between_ck_dkn = [ok for ok in other_keys if ok > ck and ok < dkn]

        all_other = [other_lines[k] for k in between_dk_ck]
        all_other.extend([other_lines[k] for k in between_ck_dkn])
        all_other_str = ' '.join(all_other)

        match = re.match(r'([\w\s]*), (.*) was arrested at (.*) on the charge\(s\) of:', all_other_str)
        if match:
            end = match.end()
            g = 0
            for ii, ao in enumerate(all_other):
                if end >= len(ao):
                    end = end - (len(ao) + 1)
                else:
                    g = ii
                    break
            datetime = pd.to_datetime(date_lines[dk],
                format='%m/%d/%y',
                errors='raise', utc=False).date()
            record = {
                'Name': match.groups()[0],
                'Date': datetime,
                'Res': match.groups()[1],
                'Location': match.groups()[2],
                'Incident': [clean_incident(i) for i in all_other[g:]],
                'Case': cno_lines[ck],
                'File': file
            }
            records.append(record)

        else:
            continue
    return records

def extract_records(lines, file=None):
    records = []
    record = None

    cno_lines = {}
    time_lines = {}
    shift_lines = {}
    date_lines = {}
    loc_lines = {}
    inc_lines = {}
    line_idx = [ cno_lines, time_lines, shift_lines, date_lines, loc_lines, inc_lines]

    case_str = "Case No.: "
    time_str = "Time: "
    shift_str = "Shift: "
    date_str = "Date Reported: "
    loc_str = "Location: "
    inc_str = "Incident: "
    strings = [ case_str, time_str, shift_str, date_str, loc_str, inc_str ]

    # Sort each line into it's own dict by line type
    for ii, line in enumerate(lines):
        for (_str, _idx) in zip(strings, line_idx):
            if line.find(_str) >= 0:
                _idx[ii] = line[line.find(_str) + len(_str):].strip()

    cno_keys = sorted(cno_lines.keys())
    cno_keys_s = cno_keys[1:] + [1e6]

    for key, key_plus in zip(cno_keys, cno_keys_s):
        time = [v for (k,v) in time_lines.items() if
                    k > key and k < key_plus]
        date = [v for (k,v) in date_lines.items() if
                    k > key and k < key_plus]
        shift = [v for (k,v) in shift_lines.items() if
                    k > key and k < key_plus]
        loc = [v for (k,v) in loc_lines.items() if
                    k > key and k < key_plus]
        incs = [v for (k,v) in inc_lines.items() if
                    k > key and k < key_plus]

        record = {}
        if file:
            record['File'] = file
        record['Case'] = cno_lines[key]
        datetime = pd.to_datetime( time[0] + ' ' + date[0],
            format='%I:%M %p %B %d, %Y',
            errors='raise', utc=False)

        new_incs = []
        for inc in incs:
            inc = clean_incident(inc)
            new_incs.append(inc)

        record['DateTime'] = datetime
        record['Shift'] = shift[0]
        record['Address'] = loc[0]
        record['Incident'] = new_incs
        records.append(record)

    return records


if __name__ == '__main__':
    s = MadisonScraper()
    s.sync_status()
    s.sync()

    s.convert_status()
    s.convert()


    incident_records = []
    arrest_records = []

    for ii, aa in enumerate(s.incidents()):
        ti = s.incident(aa)
        ti_clean = clean_report(ti)
        ti_ref = reformat_incident(ti_clean)

        for record in extract_records(ti_ref, aa):
            incident_records.append(record)


    for ii, aa in enumerate(s.arrests()):
        ta = s.arrest(aa)
        ta_clean = clean_report(ta)
        for record in extract_arrests(ta_clean, aa):
            arrest_records.append(record)

    print("Arrest Reports Found: %s" % len(s.arrests()))
    print("Incident Reports Found: %s" % len(s.incidents()))
    print("Arrest Records Found: %s" % len(arrest_records))
    print("Incident Records Found: %s" % len(incident_records))
