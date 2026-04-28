# Google Workspace OAuth2 Authorization Pulse

This skill automates OAuth2 authorization flow for Google Workspace integration.

## Purpose

Automates the OAuth2 authorization flow for Google Workspace integration:
1. Check current OAuth2 status
2. Prompt for authorization if needed
3. Refresh tokens when expired
4. Log authorization progress

## Commands

```bash
# Check OAuth2 status
python3 setup.py --check

# If not authenticated, print authorization URL
python3 setup.py --auth-url

# Exchange code for token (interactive)
python3 setup.py --auth

# Force refresh access token
python3 setup.py --refresh

# Print status to console
python3 setup.py --status

# Show recent log entries
python3 setup.py --log
```

## Environment Variables

Set these before first use:

```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export GOOGLE_REDIRECT_URI="http://localhost:8888/oauth2callback"
```

## Default Paths

- **Auth State File**: `~/.hermes/auth_state.json`
- **Log File**: `~/.hermes/logs/google-workspace.log`

## OAuth2 Scopes

By default, requests access to:
- Calendar API
- Gmail (read-only)
- Drive (read-only)
- Docs API

These scopes can be modified by changing the `SCOPES` list in the code.

## How It Works

### Initial Authorization

1. Run `python3 setup.py --auth`
2. Browser opens with Google OAuth2 consent screen
3. Click "Allow" to grant permissions
4. Copy the authorization code from the URL
5. Paste the code when prompted
6. Tokens are stored in `~/.hermes/auth_state.json`

### Automatic Refresh

The script checks token expiry and automatically refreshes when needed:
- Tokens refresh 5 minutes before expiry
- Refresh uses the stored refresh token
- New access token is saved immediately

## Logging

All operations are logged to `~/.hermes/logs/google-workspace.log` with timestamps.

## Schedule

This is designed to run every 15 minutes as a cron job:

```bash
# Add to crontab
*/15 * * * * python3 ~/skills/productivity/google-workspace/setup.py --check >> ~/.hermes/logs/cron.log 2>&1
```

## Requirements

- Python 3.8+
- Standard library only (no external dependencies)

## Troubleshooting

### "Client ID and Secret not configured"

Set environment variables:
```bash
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET="..."
```

### Token Refresh Failed

1. Check if refresh token is valid: `python3 setup.py --status`
2. Re-run authorization: `python3 setup.py --auth`
3. Verify environment variables are set

### Log Errors

View recent errors:
```bash
python3 setup.py --log
```

## Security Notes

- Access tokens are stored in plain text in `~/.hermes/auth_state.json`
- This file should be protected with proper file permissions
- The refresh token allows obtaining new access tokens
- If you suspect a security breach, revoke all tokens in Google Cloud Console

## See Also

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Workspace API Reference](https://developers.google.com/workspace/api)
