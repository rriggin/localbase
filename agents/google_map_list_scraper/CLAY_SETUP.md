# Clay.com Integration Setup Guide

This guide will help you set up Clay.com API access to import your scraped addresses.

## Prerequisites

1. **Clay.com Account**: You need an active Clay.com account
2. **API Access**: Clay.com API access (available on paid plans)

## Step 1: Get Your Clay.com API Key

1. Go to [Clay.com](https://app.clay.com) and sign in to your account
2. Navigate to **Settings** → **API**
3. Click **"Generate API Key"** or **"Create New API Key"**
4. Give your API key a name (e.g., "LocalBase Integration")
5. Copy the generated API key (it will look like: `clay_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

## Step 2: Configure Environment Variables

Add the following variable to your `.env` file:

```env
# Clay.com Configuration
CLAY_API_KEY=your_clay_api_key_here
```

Replace `your_clay_api_key_here` with the actual API key you copied from Clay.com.

## Step 3: Test the Integration

Run the Clay integration script to test the connection:

```bash
python3 clay_integration.py
```

This will:
1. Test the API connection
2. List your existing Clay tables
3. Import the scraped addresses to a new table

## Step 4: Import Your Addresses

The integration will automatically:
1. Create a new table called "Google Maps Addresses - Sedalia MO"
2. Import all 166 addresses from your CSV file
3. Provide you with a direct link to view the table in Clay

## Step 5: View Your Data in Clay

Once imported, you can:
- View your data at: `https://app.clay.com/tables/{table_id}`
- Use Clay's powerful filtering and sorting features
- Export data in various formats
- Set up automations and integrations

## Troubleshooting

### Common Issues:

1. **API Key Not Found**
   - Make sure you've added `CLAY_API_KEY` to your `.env` file
   - Verify the API key is correct and not expired

2. **Permission Denied**
   - Ensure your Clay account has API access enabled
   - Check that your API key has the necessary permissions

3. **Rate Limiting**
   - Clay has rate limits on API calls
   - If you hit limits, wait a few minutes and try again

4. **Table Creation Failed**
   - Check that your Clay workspace has space for new tables
   - Verify the table name doesn't conflict with existing tables

## Clay.com Features

Once your data is in Clay, you can:

- **Filter & Sort**: Use Clay's powerful filtering to find specific addresses
- **Enrich Data**: Use Clay's enrichment features to add phone numbers, emails, etc.
- **Export**: Export data to CSV, Excel, or other formats
- **Integrate**: Connect to other tools via Clay's integrations
- **Automate**: Set up automated workflows and data processing

## Next Steps

After importing your addresses, consider:

1. **Data Enrichment**: Use Clay's enrichment features to add contact information
2. **Lead Scoring**: Set up scoring based on address data
3. **CRM Integration**: Connect to your existing CRM systems
4. **Automated Outreach**: Set up automated email or phone campaigns

## Support

If you encounter issues:
1. Check Clay.com's [API Documentation](https://docs.clay.com/)
2. Verify your API key is valid and has proper permissions
3. Check Clay.com's status page for any service issues 