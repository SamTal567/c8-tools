"""The data and plain Python functions shared by both practice examples."""
import csv
import io
import os
from pathlib import Path

import requests

SHEET_CSV = (
    'https://docs.google.com/spreadsheets/d/'
    '1_6E97ad-AL769jA2mepnh8_hTC6AsteQRDMN4npuCyE/'
    'gviz/tq?tqx=out:csv&gid=1134972097'
)
FIELDS = {'name': 'Name', 'company': 'Company', 'interest': 'Area of interest', 'job title': 'Job title'}
HEADERS = {'Name', 'Job title', 'Company', 'Area of interest'}


def load_contacts():
    """Read the local sample, or the Google Sheet when explicitly enabled."""
    source = os.getenv('CONTACTS_SOURCE', 'local').strip().lower()
    if source == 'local':
        content = Path(__file__).with_name('contacts.csv').read_text(encoding='utf-8-sig')
    elif source == 'google':
        try:
            response = requests.get(SHEET_CSV, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ValueError('Could not read the Google Sheet. Check your connection and sheet access.') from exc
        content = response.content.decode('utf-8-sig')
    else:
        raise ValueError('CONTACTS_SOURCE must be local or google.')
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or not HEADERS.issubset(reader.fieldnames):
        raise ValueError('The contact data is unavailable or has unexpected headers. A Google Sheet must be accessible to the server.')
    return [{key: (row.get(key) or '').strip() for key in HEADERS} for row in reader]


def search_contacts(field: str, query: str) -> dict:
    """Find fictional contacts by name, company, job title, or interest."""
    field = field.strip().lower()
    query = query.strip()
    if field not in FIELDS:
        return {'error': 'Choose name, company, job title, or interest.'}
    if not query:
        return {'error': 'Enter a non-empty search term.'}
    try:
        people = load_contacts()
    except (ValueError, OSError) as exc:
        return {'error': str(exc)}
    return {'matches': [person for person in people if query.casefold() in person[FIELDS[field]].casefold()]}


def draft_connection_message(name: str) -> dict:
    """Draft a message of at most 200 characters for one fictional contact."""
    result = search_contacts('name', name)
    if 'error' in result:
        return result
    matches = result['matches']
    exact = [person for person in matches if person['Name'].casefold() == name.strip().casefold()]
    if exact:
        matches = exact
    if len(matches) != 1:
        return {'error': 'Please provide one unambiguous contact name.'}
    person = matches[0]
    first_name = person['Name'].split()[0]
    message = (f"Hi {first_name}, I'd love to connect and learn about your work "
               f"as {person['Job title']} at {person['Company']}.")
    if len(message) > 200:
        return {'error': 'The contact details are too long for a 200-character message.'}
    if person['Area of interest']:
        with_interest = message + f" I'd enjoy hearing about {person['Area of interest']}."
        if len(with_interest) <= 200:
            message = with_interest
    return {'message': message, 'characters': len(message), 'limit': 200}
