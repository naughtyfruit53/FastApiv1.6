# OAuth Token Refresh Runbook

## Overview
This runbook provides guidance for operators on handling OAuth token refresh failures in the email sync system.

## Common Issues and Resolutions
1. **REFRESH_FAILED Status**:
   - Check `last_sync_error` and `last_refresh_response` in `user_email_tokens` table for details.
   - If transient (e.g., HTTP 5xx), run manual refresh script: `python scripts/manual_refresh.py --token-id <id>`
   - If persistent, investigate provider-side issues (e.g., API outages).

2. **REAUTH_REQUIRED Status** (e.g., "invalid_grant"):
   - Notify user to re-authorize the account in the app UI.
   - Steps for user:
     - Revoke app access at https://myaccount.google.com/permissions (for Google).
     - Delete the token in app (via DELETE /api/v1/oauth/tokens/<id> or UI).
     - Re-add the email account, granting offline access.
   - After re-auth, set `sync_enabled = true` on the mail_account if needed.

3. **No Refresh Token**:
   - Indicates initial auth didn't grant offline access.
   - Follow REAUTH_REQUIRED steps above.

## Manual Refresh
Use `scripts/manual_refresh.py` for testing: