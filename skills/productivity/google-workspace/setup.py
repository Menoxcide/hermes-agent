#!/usr/bin/env python3
"""
Google Workspace OAuth2 Authorization Pulse

Automates OAuth2 authorization flow for Google Workspace integration:
- Check current OAuth2 status
- Prompt for authorization if needed
- Refresh tokens when expired
- Log authorization progress
"""

import argparse
import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, quote

# Configuration
HOME_DIR = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME_DIR, ".hermes", "logs")
AUTH_STATE_FILE = os.path.join(HOME_DIR, ".hermes", "auth_state.json")
LOG_FILE = os.path.join(LOG_DIR, "google-workspace.log")

# Google Workspace OAuth2 settings
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/docs",
]
REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8888/oauth2callback")

# Token refresh settings
TOKEN_EXPIRY_SECONDS = 3600  # 1 hour
REFRESH_THRESHOLD_SECONDS = 300  # Refresh 5 minutes before expiry

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_auth_state():
    """Load current authentication state from file."""
    if os.path.exists(AUTH_STATE_FILE):
        try:
            with open(AUTH_STATE_FILE, "r") as f:
                state = json.load(f)
            logger.info("Loaded auth state from file")
            return state
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load auth state: {e}")
            return None
    return None


def save_auth_state(state):
    """Save authentication state to file."""
    try:
        with open(AUTH_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        logger.info("Saved auth state to file")
        return True
    except IOError as e:
        logger.error(f"Failed to save auth state: {e}")
        return False


def get_oauth2_status():
    """Check current OAuth2 authentication status."""
    state = load_auth_state()
    
    if not state:
        return {
            "status": "unauthorized",
            "message": "No authentication state found",
            "tokens": None
        }
    
    # Check token expiry
    access_token = state.get("access_token")
    refresh_token = state.get("refresh_token")
    expiry_timestamp = state.get("expiry_timestamp")
    
    if not access_token or not refresh_token:
        return {
            "status": "incomplete",
            "message": "Authentication state exists but tokens are missing",
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiry_timestamp": expiry_timestamp
            }
        }
    
    if expiry_timestamp:
        current_time = time.time()
        time_remaining = expiry_timestamp - current_time
        
        if time_remaining <= 0:
            return {
                "status": "expired",
                "message": f"Access token has expired ({time_remaining:.1f}s remaining)",
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expiry_timestamp": expiry_timestamp
                }
            }
    else:
        return {
            "status": "valid",
            "message": "Valid authentication tokens present",
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiry_timestamp": expiry_timestamp
            }
        }
    
    return {
        "status": "unknown",
        "message": "Unable to determine token status",
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expiry_timestamp": expiry_timestamp
        }
    }


def generate_auth_url():
    """Generate OAuth2 authorization URL for user to authorize access."""
    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "state": str(int(time.time())),
        "access_type": "offline",
        "prompt": "consent"
    }
    
    url = f"https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(auth_params)
    return url


def exchange_code_for_token(code):
    """Exchange authorization code for access and refresh tokens."""
    import secrets
    
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("Client ID and Secret not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
        return None
    
    auth_state = load_auth_state() or {}
    
    # Generate unique state for callback verification
    auth_state["state"] = str(int(time.time()))
    auth_state["authorization_url"] = generate_auth_url()
    save_auth_state(auth_state)
    
    token_params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": code,
        "state": auth_state.get("state")
    }
    
    token_url = "https://oauth2.googleapis.com/token"
    
    try:
        req_data = urlencode(token_params).encode("utf-8")
        req = urllib.request.Request(
            token_url,
            data=req_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            tokens = json.loads(response.read().decode("utf-8"))
            
            # Save tokens to state
            auth_state.update({
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "expiry_timestamp": int(time.time()) + int(tokens.get("expires_in", 3600)),
                "token_received": True
            })
            save_auth_state(auth_state)
            
            logger.info("Successfully exchanged code for tokens")
            return tokens
            
    except urllib.error.HTTPError as e:
        logger.error(f"Failed to exchange code for token: {e.code} - {e.reason}")
        return None
    except Exception as e:
        logger.error(f"Error exchanging code for token: {e}")
        return None


def refresh_access_token():
    """Refresh the access token using the refresh token."""
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("Client ID and Secret not configured.")
        return False
    
    state = load_auth_state()
    if not state or "refresh_token" not in state:
        logger.error("No refresh token available")
        return False
    
    refresh_params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": state["refresh_token"],
        "grant_type": "refresh_token"
    }
    
    refresh_url = "https://oauth2.googleapis.com/token"
    
    try:
        req_data = urlencode(refresh_params).encode("utf-8")
        req = urllib.request.Request(
            refresh_url,
            data=req_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            tokens = json.loads(response.read().decode("utf-8"))
            
            # Update state with new tokens
            auth_state = load_auth_state()
            auth_state.update({
                "access_token": tokens.get("access_token"),
                "expiry_timestamp": int(time.time()) + int(tokens.get("expires_in", 3600))
            })
            save_auth_state(auth_state)
            
            logger.info("Successfully refreshed access token")
            return tokens
            
    except urllib.error.HTTPError as e:
        logger.error(f"Failed to refresh token: {e.code} - {e.reason}")
        return False
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return False


def authorize_interactive():
    """Interactive authorization flow for user."""
    logger.info("=" * 60)
    logger.info("Google Workspace OAuth2 Authorization")
    logger.info("=" * 60)
    
    state = load_auth_state()
    
    if state and state.get("authorization_url"):
        url = state["authorization_url"]
        logger.info(f"Please visit the following URL in your browser:")
        logger.info(f"\n{url}")
        logger.info("\n1. Click 'Allow' to grant Google Workspace access")
        logger.info("2. Copy the authorization code from the URL")
        logger.info("3. Paste the code when prompted")
        logger.info("\nPress Enter when you have the code...")
        input()
    else:
        url = generate_auth_url()
        logger.info(f"Please visit: {url}")
        logger.info("1. Click 'Allow' to grant Google Workspace access")
        logger.info("2. Copy the authorization code from the URL")
        logger.info("3. Press Enter when you have the code...")
        input()
    
    # Get the authorization code from user
    logger.info("\nEnter the authorization code (or press Enter to use the interactive flow):")
    code = input("Authorization code: ").strip()
    
    if not code:
        logger.info("Starting interactive authorization...")
        import webbrowser
        import time
        
        url = generate_auth_url()
        print(f"Opening browser to: {url}")
        webbrowser.open(url)
        
        print("\n" + "=" * 60)
        print("IMPORTANT: After granting permission, the URL will contain")
        print("a 'code=' parameter. Copy the entire URL and press Enter:")
        print("=" * 60 + "\n")
        
        time.sleep(5)
    
    # Exchange code for tokens
    logger.info(f"\nExchanging code: {code[:20]}...")
    result = exchange_code_for_token(code)
    
    if result:
        logger.info("\n" + "=" * 60)
        logger.info("SUCCESS! Authorization complete!")
        logger.info("=" * 60)
        logger.info(f"Access Token: {result.get('access_token', 'N/A')[:20]}...")
        logger.info(f"Refresh Token: {result.get('refresh_token', 'N/A')[:20]}...")
        logger.info("\nYour Google Workspace OAuth2 credentials are now stored.")
        logger.info("You can use these to access Google Workspace APIs.")
        return True
    else:
        logger.error("Authorization failed. Please try again.")
        return False


def check_and_refresh_tokens():
    """Automatically check and refresh tokens if needed."""
    status = get_oauth2_status()
    
    logger.info(f"OAuth2 Status: {status['status']}")
    logger.info(f"Message: {status['message']}")
    
    if status["status"] == "expired":
        logger.info("Access token expired. Refreshing...")
        success = refresh_access_token()
        if success:
            logger.info("Token refreshed successfully")
            return True
        else:
            logger.error("Failed to refresh token")
            return False
    elif status["status"] == "valid":
        logger.info("Tokens are valid. No action needed.")
        return True
    else:
        logger.info("No action required (unauthorized or incomplete)")
        return False


def print_status():
    """Print current OAuth2 status to console."""
    status = get_oauth2_status()
    
    print("\n" + "=" * 60)
    print("Google Workspace OAuth2 Status")
    print("=" * 60)
    print(f"Status: {status['status'].upper()}")
    print(f"Message: {status['message']}")
    
    if status.get("tokens"):
        tokens = status["tokens"]
        print("\nTokens:")
        print(f"  Access Token: {'*' * 10}{''.join(list(tokens.get('access_token', '')[:10]))}{'*' * 10}")
        print(f"  Refresh Token: {'*' * 10}{''.join(list(tokens.get('refresh_token', '')[:10]))}{'*' * 10}")
        
        if tokens.get("expiry_timestamp"):
            expiry = datetime.fromtimestamp(tokens["expiry_timestamp"])
            print(f"  Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
            description="Google Workspace OAuth2 Authorization Pulse",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Commands:
  --check              Check current OAuth2 status (default)
  --auth-url           Print authorization URL for manual authorization
  --auth               Perform interactive authorization flow
  --refresh            Force refresh access token
  --status             Print status to console
  --log                Show recent log entries

Examples:
  python3 setup.py --check
  python3 setup.py --auth-url
  python3 setup.py --auth
  python3 setup.py --refresh
  python3 setup.py --status
"""
    )
    
    parser.add_argument(
            "--check",
            action="store_true",
            help="Check current OAuth2 status (default)"
    )
    parser.add_argument(
            "--auth-url",
            action="store_true",
            help="Print authorization URL for manual authorization"
    )
    parser.add_argument(
            "--auth",
            action="store_true",
            help="Perform interactive authorization flow"
    )
    parser.add_argument(
            "--refresh",
            action="store_true",
            help="Force refresh access token"
    )
    parser.add_argument(
            "--status",
            action="store_true",
            help="Print status to console"
    )
    parser.add_argument(
            "--log",
            action="store_true",
            help="Show recent log entries"
    )
    
    args = parser.parse_args()
    
    if args.log:
        # Show recent log entries
        logger.info("Recent log entries:")
        logger.info("-" * 60)
        try:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()[-50:]
                for line in lines:
                    logger.info(line.strip())
        except IOError as e:
            logger.error(f"Cannot read log file: {e}")
        return
    
    if args.check:
        status = get_oauth2_status()
        print(f"OAuth2 Status: {status['status']}")
        print(f"Message: {status['message']}")
        if status.get("tokens"):
            print(f"Tokens: {status['tokens']}")
        return
    
    if args.auth_url:
        url = generate_auth_url()
        print(f"Authorization URL:\n{url}")
        return
    
    if args.auth:
        authorize_interactive()
        return
    
    if args.refresh:
        success = refresh_access_token()
        if success:
            print("Token refreshed successfully!")
        else:
            print("Failed to refresh token!")
        return
    
    if args.status:
        print_status()
        return
    
    # Default: check status
    status = get_oauth2_status()
    print(f"\nGoogle Workspace OAuth2 Status")
    print(f"Status: {status['status']}")
    print(f"Message: {status['message']}")
    if status.get("tokens"):
        print(f"Tokens: {status['tokens']}")


if __name__ == "__main__":
    main()
