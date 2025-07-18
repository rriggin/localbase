#!/usr/bin/env python3
"""
Enhanced Zapier Batch Processor for Clay Integration
Handles processing of all 1,020+ addresses from the CSV data
"""

import csv
import io
import json

def process_csv_for_batch_import():
    """
    Process CSV for batch import to Clay
    This replaces the simple parser in your Zapier "Code by Zapier" step
    """
    
    # Get the CSV data from the previous step
    csv_data = input_data.get('csv_content', '')
    
    # Parse the CSV
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    # Initialize output
    output = {}
    all_records = []
    
    # Process all rows
    for i, row in enumerate(csv_reader):
        record = {}
        for column_name, value in row.items():
            # Clean column name for Zapier
            clean_column = column_name.replace(' ', '_').replace('-', '_').replace('.', '_')
            clean_value = str(value).strip() if value else ''
            record[clean_column] = clean_value
        
        all_records.append(record)
        
        # Also create individual record outputs (for backward compatibility)
        if i < 10:  # Only create individual outputs for first 10 records to avoid Zapier limits
            for column_name, value in record.items():
                output[f'record_{i}_{column_name}'] = value
    
    # Add batch data
    output['total_records'] = len(all_records)
    output['batch_size'] = min(50, len(all_records))  # Process in batches of 50
    output['total_batches'] = (len(all_records) + 49) // 50  # Ceiling division
    
    # Create batches for processing
    batch_size = 50
    for batch_num in range(0, min(10, (len(all_records) + batch_size - 1) // batch_size)):  # Limit to 10 batches for Zapier
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, len(all_records))
        batch_records = all_records[batch_start:batch_end]
        
        # Create JSON string for this batch
        batch_json = json.dumps(batch_records)
        output[f'batch_{batch_num}_json'] = batch_json
        output[f'batch_{batch_num}_count'] = len(batch_records)
        
        # Also create individual fields for first record in each batch (for mapping)
        if batch_records:
            first_record = batch_records[0]
            for field_name, field_value in first_record.items():
                output[f'batch_{batch_num}_sample_{field_name}'] = field_value
    
    return output

# Alternative: Single Record Iterator
def process_csv_single_record():
    """
    Alternative approach: Process one record at a time
    This creates multiple Zap runs, one for each record
    """
    
    csv_data = input_data.get('csv_content', '')
    record_index = int(input_data.get('record_index', 0))  # Which record to process
    
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    all_records = list(csv_reader)
    
    output = {'total_records': len(all_records)}
    
    if record_index < len(all_records):
        record = all_records[record_index]
        
        # Clean and output current record
        for column_name, value in record.items():
            clean_column = column_name.replace(' ', '_').replace('-', '_').replace('.', '_')
            clean_value = str(value).strip() if value else ''
            output[f'current_{clean_column}'] = clean_value
        
        output['current_record_index'] = record_index
        output['has_more_records'] = record_index + 1 < len(all_records)
        output['next_record_index'] = record_index + 1
    else:
        output['has_more_records'] = False
        output['current_record_index'] = -1
    
    return output

# Main processing function (use this in Zapier)
# Choose one of the approaches above based on your preference

# For batch processing (recommended):
output = process_csv_for_batch_import()

# For single record processing:
# output = process_csv_single_record() 