import csv
import io

# Get the CSV data from the previous step
csv_data = input_data.get('csv_content', '')

# Parse the CSV
csv_reader = csv.DictReader(io.StringIO(csv_data))

# Convert to list
all_records = list(csv_reader)

# Get the current iteration (starts at 0)
# This will be managed by running the zap multiple times
current_index = 0  # You can modify this to process different records

# Output just one record at a time
if current_index < len(all_records):
    row = all_records[current_index]
    output = {}
    
    # Clean and output current record
    for column_name, value in row.items():
        clean_column = column_name.replace(' ', '_').replace('-', '_').replace('.', '_')
        clean_value = str(value).strip() if value else ''
        output[clean_column] = clean_value
    
    # Add metadata
    output['current_record_number'] = current_index + 1
    output['total_records'] = len(all_records)
    output['records_remaining'] = len(all_records) - (current_index + 1)
    output['is_last_record'] = (current_index == len(all_records) - 1)

else:
    # No more records
    output = {
        'message': 'All records processed',
        'total_records': len(all_records),
        'current_record_number': 0,
        'records_remaining': 0,
        'is_last_record': True
    } 