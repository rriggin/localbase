from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# === CONFIG ===
AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN', 'patKD6cxWXpRuYzoY.9ac26e903fb5bb7323f78db66c2f036179d9b6b339cef7d4c9c0156cbd8b5987')
BASE_ID = os.getenv('BASE_ID', 'app9Mj5rbIFvK9p9D')
TABLE_NAME = os.getenv('TABLE_NAME', 'Leads')

HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_TOKEN}',
    'Content-Type': 'application/json'
}

def fetch_records():
    """Fetch all records from Airtable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    params = {'pageSize': 100}
    records = []
    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        records.extend(data['records'])
        url = data.get('offset', None)
        if url:
            url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?offset={url}'
    return records

def update_records(records_to_update):
    """Update records in Airtable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    for i in range(0, len(records_to_update), 10):  # Airtable batch limit
        batch = records_to_update[i:i + 10]
        payload = {'records': batch}
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'LocalBase API is running'})

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all leads from Airtable"""
    try:
        records = fetch_records()
        return jsonify({
            'success': True,
            'count': len(records),
            'leads': records
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leads/empty-names', methods=['GET'])
def get_leads_with_empty_names():
    """Get leads that have empty names"""
    try:
        records = fetch_records()
        empty_name_records = []
        
        for record in records:
            name = record['fields'].get('Name', '')
            if isinstance(name, str) and name.strip() == '':
                empty_name_records.append(record)
        
        return jsonify({
            'success': True,
            'count': len(empty_name_records),
            'leads': empty_name_records
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leads/update-empty-names', methods=['POST'])
def update_empty_names():
    """Update leads with empty names"""
    try:
        records = fetch_records()
        to_update = []

        for record in records:
            name = record['fields'].get('Name', '')
            if isinstance(name, str) and name.strip() == '':
                to_update.append({
                    'id': record['id'],
                    'fields': {'Name': ''}
                })

        if to_update:
            update_records(to_update)
            return jsonify({
                'success': True,
                'message': f'Updated {len(to_update)} records with empty names',
                'updated_count': len(to_update)
            })
        else:
            return jsonify({
                'success': True,
                'message': 'No records needed updating',
                'updated_count': 0
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leads/<record_id>', methods=['GET'])
def get_lead(record_id):
    """Get a specific lead by ID"""
    try:
        url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/{record_id}'
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return jsonify({
            'success': True,
            'lead': response.json()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/leads/<record_id>', methods=['PATCH'])
def update_lead(record_id):
    """Update a specific lead by ID"""
    try:
        data = request.get_json()
        if not data or 'fields' not in data:
            return jsonify({
                'success': False,
                'error': 'Fields data is required'
            }), 400
        
        url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}/{record_id}'
        payload = {'fields': data['fields']}
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        return jsonify({
            'success': True,
            'message': 'Lead updated successfully',
            'lead': response.json()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 