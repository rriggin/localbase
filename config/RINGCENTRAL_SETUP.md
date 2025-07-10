# RingCentral API Setup Guide

This guide will help you set up RingCentral API access to fetch call logs and analyze call durations.

## Prerequisites

1. **RingCentral Account**: You need an active RingCentral account with admin access
2. **Developer Account**: Access to RingCentral Developer Console

## Step 1: Create a RingCentral App

1. Go to [RingCentral Developer Console](https://developers.ringcentral.com/)
2. Sign in with your RingCentral account
3. Click "Create App"
4. Choose "Other (Non-UI)" as the app type
5. Fill in the app details:
   - **App Name**: LocalBase Call Analytics
   - **App Type**: Other (Non-UI)
   - **Platform Type**: Other
6. Click "Create"

## Step 2: Configure App Permissions

1. In your app dashboard, go to "Permissions"
2. Add the following permissions:
   - `ReadAccounts` - Read account information
   - `ReadCallLog` - Read call logs
   - `ReadCallLog` - Read call log entries
   - `ReadPresence` - Read presence information

## Step 3: Get Your Credentials

1. In your app dashboard, go to "Credentials"
2. Note down:
   - **Client ID**
   - **Client Secret**
3. Go to "Settings" and note down:
   - **Account ID** (found in the URL or account settings)

## Step 4: Configure Environment Variables

Add the following variables to your `.env` file:

```env
# RingCentral API Credentials
RINGCENTRAL_CLIENT_ID=your_client_id_here
RINGCENTRAL_CLIENT_SECRET=your_client_secret_here
RINGCENTRAL_USERNAME=your_phone_number_or_extension
RINGCENTRAL_PASSWORD=your_password
RINGCENTRAL_ACCOUNT_ID=your_account_id_here
```

### Notes:
- **RINGCENTRAL_USERNAME**: Use your RingCentral phone number (e.g., +1234567890) or extension number
- **RINGCENTRAL_PASSWORD**: Your RingCentral account password
- **RINGCENTRAL_ACCOUNT_ID**: Your RingCentral account ID (found in account settings)

## Step 5: Test the Integration

Run the RingCentral API script:

```bash
python3 ringcentral_api.py
```

## Troubleshooting

### Common Issues:

1. **Authentication Failed**
   - Verify your credentials are correct
   - Ensure your app has the required permissions
   - Check that your account is active

2. **Permission Denied**
   - Make sure your app has `ReadCallLog` permission
   - Verify you're using an admin account or have appropriate access

3. **No Call Logs Returned**
   - Check the date range (default is last 7 days)
   - Ensure there are calls in the specified time period
   - Verify the account ID is correct

## API Endpoints Used

- **Authentication**: `POST /restapi/oauth/token`
- **Call Logs**: `GET /restapi/v1.0/account/{accountId}/extension/~/call-log`

## Data Retrieved

The API will fetch:
- Call direction (Inbound/Outbound)
- Phone numbers (from/to)
- Call duration (in seconds)
- Call result (Answered/Missed/etc.)
- Timestamp
- Extension information

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for all sensitive credentials
- Consider using RingCentral's JWT authentication for production use
- Regularly rotate your client secret 