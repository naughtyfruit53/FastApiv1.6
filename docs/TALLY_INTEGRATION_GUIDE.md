# Tally Integration User Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
4. [Configuration](#configuration)
5. [Synchronization](#synchronization)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

## Overview

The Tally Integration feature allows you to synchronize data between your FastAPI application and Tally ERP. This enables real-time data exchange for:
- Chart of Accounts / Ledgers
- Vouchers (Sales, Purchase, Payment, Receipt, etc.)
- Inventory Items
- Customer and Vendor Master Data
- Stock Transactions

## Prerequisites

Before setting up Tally integration, ensure you have:

1. **Tally ERP 9 or TallyPrime** installed and running
2. **Tally configured with ODBC/HTTP server enabled**
   - Go to Gateway of Tally → F11 (Features) → F3 (Company Features)
   - Enable "Enable Tally as Server" option
   - Set port number (default: 9000)
3. **Network connectivity** between the application server and Tally server
4. **App Super Admin access** in the FastAPI application
5. **Company data loaded** in Tally with proper financial year

## Setup Instructions

### Step 1: Enable Tally HTTP Server

1. Open Tally on your system
2. Navigate to: **Gateway of Tally** → **F11: Features** → **F3: Company Features**
3. Set **Enable Tally as Server** to **Yes**
4. Configure the following:
   - **Port**: 9000 (default) or your custom port
   - **Allowed IP Addresses**: Add the IP address of your application server
   - **Security**: Enable if you want password protection
5. Save the configuration

### Step 2: Configure Tally Integration in Application

1. Log in to the application as **App Super Admin**
2. Navigate to **Settings** → **Organization Settings**
3. Scroll down to the **Tally Integration** section
4. Toggle **Enable Tally Sync** to ON
5. Click **Configure** button

### Step 3: Enter Tally Connection Details

In the Tally Configuration dialog, enter:

| Field | Description | Example |
|-------|-------------|---------|
| **Tally Server Host** | IP address or hostname where Tally is running | `localhost` or `192.168.1.100` |
| **Port** | Port number configured in Tally | `9000` (default) |
| **Company Name** | Exact name of the company in Tally | `ABC Traders` |
| **Sync Frequency** | How often to sync (currently manual only) | `Manual` |

### Step 4: Test Connection

1. After entering the details, click **Test Connection**
2. Wait for the connection test to complete
3. If successful, you'll see a success message with Tally version info
4. If failed, check the [Troubleshooting](#troubleshooting) section

### Step 5: Save Configuration

1. Click **Save** to store the configuration
2. The Tally integration is now ready to use

## Configuration

### Network Configuration

#### Same Machine Setup
If Tally is running on the same machine as the application:
- Host: `localhost` or `127.0.0.1`
- Port: `9000` (default)

#### Different Machine Setup
If Tally is running on a different machine:
- Host: IP address of the Tally machine (e.g., `192.168.1.100`)
- Port: `9000` (default)
- Ensure firewall allows incoming connections on port 9000

#### Cloud/VPN Setup
If accessing Tally over VPN or cloud:
- Host: Public IP or VPN IP of Tally server
- Port: Mapped port (may differ from 9000)
- Ensure proper port forwarding is configured

### Security Considerations

1. **Network Security**
   - Use VPN for remote access
   - Configure firewall rules to restrict access
   - Use IP whitelisting in Tally settings

2. **Data Security**
   - Enable Tally security if handling sensitive data
   - Use HTTPS for application access
   - Regular backups of both systems

## Synchronization

### Manual Sync

1. Navigate to **Settings** → **Organization Settings**
2. Scroll to **Tally Integration** section
3. Click **Sync Now** button
4. Wait for sync to complete
5. Check the **Last synced** timestamp

### What Gets Synced?

#### From Tally to Application:
- Chart of Accounts (Ledgers)
- Stock Items
- Vouchers (historical data)
- Customer/Vendor details
- Opening balances

#### From Application to Tally:
- New vouchers created in application
- New ledgers created in application
- Stock updates from application
- Customer/Vendor additions

### Sync Process

The synchronization follows this order:
1. **Master Data Sync**: Ledgers, Items, Parties
2. **Voucher Data Sync**: Historical vouchers
3. **Stock Sync**: Current stock levels
4. **Reconciliation**: Match and update records

### Sync Status

After each sync, you'll see:
- Total records synced
- Number of new records created
- Number of existing records updated
- Any errors or warnings

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Connection Failed
**Symptom**: "Unable to connect to Tally server" error

**Solutions**:
1. Verify Tally is running and company is loaded
2. Check if Tally HTTP server is enabled (F11 → F3)
3. Confirm port number matches (default: 9000)
4. Test network connectivity: `telnet <tally-host> 9000`
5. Check firewall settings on both machines
6. Verify IP address/hostname is correct

#### Issue 2: Company Not Found
**Symptom**: "Company name not found in Tally" error

**Solutions**:
1. Verify exact company name in Tally (case-sensitive)
2. Ensure company is loaded in Tally
3. Check if company data is corrupted
4. Try with a different company to test

#### Issue 3: Sync Fails Midway
**Symptom**: Sync starts but stops partway through

**Solutions**:
1. Check Tally system resources (CPU, memory)
2. Verify Tally data integrity
3. Check application logs for specific errors
4. Try syncing in smaller batches
5. Restart Tally and try again

#### Issue 4: Duplicate Records
**Symptom**: Same records appear multiple times

**Solutions**:
1. Check record matching criteria
2. Verify voucher numbers are unique
3. Review master data duplicate detection
4. Run data cleanup in both systems

#### Issue 5: Slow Sync Performance
**Symptom**: Sync takes very long time

**Solutions**:
1. Reduce sync scope (date range or record type)
2. Optimize Tally database (F11 → F3 → Database → Optimize)
3. Check network bandwidth
4. Increase Tally memory allocation
5. Schedule sync during off-peak hours

### Getting Debug Information

To get detailed logs for troubleshooting:

1. **Application Logs**:
   - Check backend logs in `logs/` directory
   - Look for Tally-related error messages

2. **Tally Logs**:
   - Check Tally's log file
   - Enable Tally logging if not already enabled

3. **Network Logs**:
   - Use Wireshark or tcpdump to capture network traffic
   - Verify HTTP requests/responses

## FAQ

### Q1: Can I use Tally Cloud with this integration?
**A**: Yes, if you have access to the Tally Cloud API endpoint. Configure the host and port accordingly.

### Q2: Does this work with Tally.ERP 9 and TallyPrime?
**A**: Yes, the integration supports both Tally.ERP 9 (Release 6.0 onwards) and TallyPrime.

### Q3: Can multiple users sync simultaneously?
**A**: It's recommended to have only one sync process at a time to avoid conflicts. The system will queue sync requests.

### Q4: What happens if Tally crashes during sync?
**A**: The sync will fail and can be retried. No data will be corrupted as changes are committed only after successful sync.

### Q5: Can I sync specific voucher types only?
**A**: Currently, the sync is comprehensive. Selective sync by voucher type is planned for future releases.

### Q6: How do I handle sync conflicts?
**A**: The system follows "last write wins" principle. Manual reconciliation may be needed for conflicting records.

### Q7: Is there a sync size limit?
**A**: There's no hard limit, but very large datasets (>100K records) should be synced in batches for best performance.

### Q8: Can I undo a sync?
**A**: Sync operations are not automatically reversible. Maintain regular backups of both systems before syncing.

### Q9: Does this require internet connection?
**A**: Only if Tally is on a different network. Local network sync doesn't need internet.

### Q10: What data format does the integration use?
**A**: The integration uses Tally's XML/ODBC interface for data exchange.

## Support

For additional help:
- Check application logs for detailed error messages
- Contact your system administrator
- Refer to Tally documentation for Tally-specific issues
- Review FastAPI application documentation

## Version History

- **v1.0** (Current): Initial Tally integration release
  - Manual sync support
  - Basic master data and voucher sync
  - Connection testing

## Future Enhancements

Planned features for future releases:
- Automatic scheduled sync
- Selective voucher type sync
- Real-time sync (webhook-based)
- Two-way conflict resolution
- Sync analytics and reporting
- Multi-company sync support
