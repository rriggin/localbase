# Clay Field Mapping Guide for 1,020+ Addresses

## Overview
This guide shows you exactly how to update your Zapier workflow to handle all 1,020 addresses from the Winterset-Longview list with proper field mappings to Clay.

## 📋 Prerequisites
- Your Zapier workflow is already set up with 4 steps
- You have access to edit the Zap
- Your Clay table exists and has the appropriate columns

## 🔧 Step 1: Update Zapier Code Parser

### 1.1: Go to Your Zapier Dashboard
1. Open [zapier.com](https://zapier.com)
2. Find your "Fetch Localbase Google Maps List from Gist >> Send to Clay" Zap
3. Click **"Edit Zap"**

### 1.2: Update Step 3 (Code by Zapier)
1. Click on **Step 3: "Code by Zapier"**
2. Click **"Edit"** 
3. **Replace the entire code** with this new version:

```python
import csv
import io
import json

# Get the CSV data from the previous step
csv_data = input_data.get('csv_content', '')

# Parse the CSV
csv_reader = csv.DictReader(io.StringIO(csv_data))

# Initialize output dictionary
output = {}
all_records = []

# Process all rows
for i, row in enumerate(csv_reader):
    record = {}
    for column_name, value in row.items():
        # Clean column name for Zapier (remove spaces, special chars)
        clean_column = column_name.replace(' ', '_').replace('-', '_').replace('.', '_')
        clean_value = str(value).strip() if value else ''
        record[clean_column] = clean_value
    
    all_records.append(record)

# Add summary info
output['total_records'] = len(all_records)

# Create batch processing outputs
# Clay can handle bulk imports, so we'll create JSON batches
batch_size = 100  # Adjust based on Clay's limits
total_batches = (len(all_records) + batch_size - 1) // batch_size

for batch_num in range(min(10, total_batches)):  # Limit to 10 batches for Zapier output limits
    batch_start = batch_num * batch_size
    batch_end = min(batch_start + batch_size, len(all_records))
    batch_records = all_records[batch_start:batch_end]
    
    # Create JSON for this batch
    output[f'batch_{batch_num}_json'] = json.dumps(batch_records)
    output[f'batch_{batch_num}_count'] = len(batch_records)

# Also create individual record outputs for the first 10 records (for testing/mapping)
for i in range(min(10, len(all_records))):
    record = all_records[i]
    for field_name, field_value in record.items():
        output[f'record_{i}_{field_name}'] = field_value

# Create easy-to-map outputs for the first record (most common use case)
if all_records:
    first_record = all_records[0]
    for field_name, field_value in first_record.items():
        output[f'first_{field_name}'] = field_value
```

4. Click **"Test"** to run the updated code
5. You should see outputs like:
   - `total_records: 1020`
   - `first_name`, `first_address`, `first_street_address`, etc.
   - `batch_0_json`, `batch_1_json`, etc.

## 🎯 Step 2: Update Clay Field Mappings

### 2.1: Go to Step 4 (Clay Integration)
1. Click on **Step 4: "Clay - Create Record in Table"**
2. Click **"Edit"**

### 2.2: Map Individual Record Fields (Option A - Single Record)

If you want to process one record at a time, map these fields:

```
Clay Table Column          →    Zapier Variable
─────────────────────────────────────────────────────
Name                      →    first_name
Full Address              →    first_address  
Street Address            →    first_street_address
City                      →    first_city
State                     →    first_state
ZIP Code                  →    first_zip_code
Source                    →    first_source
Import Date               →    first_import_date
Import Time               →    first_import_time
```

### 2.3: Set Up Bulk Import (Option B - Recommended)

**For processing all 1,020 records**, you have two approaches:

#### Approach 1: Multiple Clay Actions
1. **Duplicate Step 4** nine more times (for 10 total Clay steps)
2. **Map each step** to a different batch:
   - Step 4a: Map to `batch_0_json` 
   - Step 4b: Map to `batch_1_json`
   - Step 4c: Map to `batch_2_json`
   - etc.

#### Approach 2: Clay Bulk Import (Preferred)
1. Check if Clay has a **"Bulk Import"** or **"Import CSV"** action
2. If available, map the entire batch to Clay:
   - **CSV Data**: `batch_0_json`
   - **Format**: JSON
   - **Records**: `batch_0_count`

### 2.4: Essential Field Mappings

For your Clay table, ensure you have these columns and mappings:

```
Required Clay Columns:
┌─────────────────┬─────────────────────┬──────────────────────┐
│ Clay Column     │ Type                │ Zapier Variable      │
├─────────────────┼─────────────────────┼──────────────────────┤
│ Name            │ Text                │ first_name           │
│ Address         │ Text                │ first_address        │
│ Street Address  │ Text                │ first_street_address │
│ City            │ Text                │ first_city           │
│ State           │ Text (2 char)       │ first_state          │
│ ZIP Code        │ Text/Number         │ first_zip_code       │
│ Full Address    │ Text                │ first_full_address   │
│ Source          │ Text                │ first_source         │
│ Import Date     │ Date                │ first_import_date    │
│ Import Time     │ Time                │ first_import_time    │
│ Record Count    │ Number              │ total_records        │
└─────────────────┴─────────────────────┴──────────────────────┘
```

## 🔄 Step 3: Handle Multiple Records

### Option A: Looping (If Clay Supports It)
1. In Clay action, look for **"Loop"** or **"Multiple Records"** option
2. Set loop source to: `batch_0_json`
3. Map fields using loop variables:
   - Name: `{{item.name}}`
   - Address: `{{item.address}}`
   - etc.

### Option B: Multiple Zap Runs
1. Create a **new trigger** that processes record by record
2. Use **Zapier's "Delay"** action between records
3. Process 1 record every few seconds to avoid rate limits

### Option C: Manual Batch Processing
1. **Test with first batch** (`batch_0_json`)
2. **Manually trigger Zap** for each batch
3. **Monitor Clay table** for successful imports

## ✅ Step 4: Test the Integration

### 4.1: Test With Sample Data
1. Click **"Test"** on your Clay action
2. Verify the first record imports correctly
3. Check Clay table for the new record

### 4.2: Full Test Run
1. Click **"Test Zap"** at the top
2. Monitor all 4 steps for success
3. Check your Clay table for records

### 4.3: Expected Results
After successful test:
- ✅ **Total records processed**: 1,020
- ✅ **Clay table updated** with Winterset-Longview addresses  
- ✅ **All 10 columns** mapped correctly
- ✅ **Addresses from Lee's Summit, MO 64081**

## 🚨 Troubleshooting

### Common Issues:

**1. "Too many output variables"**
- **Solution**: The new code limits to 10 batches to avoid this

**2. "Clay API rate limit"**
- **Solution**: Add delays between Clay actions or use bulk import

**3. "Field mapping errors"**
- **Solution**: Check that Clay table has all required columns

**4. "JSON parsing errors"**
- **Solution**: Verify CSV format is correct in gist

### Debug Steps:
1. **Check Step 2 output**: Verify CSV is being fetched
2. **Check Step 3 output**: Verify JSON batches are created  
3. **Check Step 4 mapping**: Verify all fields are mapped correctly
4. **Check Clay table**: Verify columns exist and match

## 🎉 Final Activation

Once testing is successful:

1. **Turn on the Zap**: Toggle from "Off" to "On"
2. **Set schedule**: Confirm it runs every 15 minutes
3. **Monitor initial runs**: Check Clay table after first few runs
4. **Verify data quality**: Check that addresses look correct

## 📊 Expected Final Result

Your Clay table will have:
- **1,020+ addresses** from Winterset-Longview list
- **All in Lee's Summit, MO 64081** area
- **Complete address breakdown** (street, city, state, ZIP)
- **Source tracking** and import timestamps
- **Automatic updates** every 15 minutes if gist changes

## 🔄 Batch Processing Summary

The new system processes records in these outputs:
- `batch_0_json`: Records 1-100
- `batch_1_json`: Records 101-200  
- `batch_2_json`: Records 201-300
- etc. (up to 10 batches = 1,000 records)

Each batch contains properly formatted JSON that Clay can import directly.

---

**Need help with any of these steps?** Test each step individually and check the outputs before proceeding to the next step. 