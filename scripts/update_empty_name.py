import requests

# === CONFIG ===
AIRTABLE_TOKEN = 'patKD6cxWXpRuYzoY.9ac26e903fb5bb7323f78db66c2f036179d9b6b339cef7d4c9c0156cbd8b5987'
BASE_ID = 'app9Mj5rbIFvK9p9D'
TABLE_NAME = 'Leads'

HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_TOKEN}',
    'Content-Type': 'application/json'
}

def fetch_records():
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
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    for i in range(0, len(records_to_update), 10):  # Airtable batch limit
        batch = records_to_update[i:i + 10]
        payload = {'records': batch}
        response = requests.patch(url, headers=HEADERS, json=payload)
        response.raise_for_status()

def main():
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
        print(f"Updating {len(to_update)} records...")
        update_records(to_update)
        print("Done.")
    else:
        print("No records needed updating.")

if __name__ == '__main__':
    main()

