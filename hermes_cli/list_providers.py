#!/usr/bin/env python3
"""
Hermes CLI - Providers Command
List all configured providers and their available models with free tier detection.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import urllib.request
import urllib.error

# Hermes home directory
HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
DEFAULT_CONFIG = HERMES_HOME / 'config.yaml'

def get_env_var(value: str) -> Optional[str]:
    """Extract environment variable value."""
    if not value:
        return None
    if value.startswith('env:'):
        env_name = value[4:]
        return os.environ.get(env_name)
    return value

def fetch_openrouter_models(api_key: Optional[str]) -> List[Dict]:
    """Fetch models from OpenRouter API."""
    url = 'https://openrouter.ai/api/v1/models'
    headers = {'Accept': 'application/json'}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get('data', [])
    except Exception as e:
        return []

def fetch_ollama_models(base_url: str) -> List[Dict]:
    """Fetch models from local Ollama instance."""
    url = f"{base_url.rstrip('/v1')}/api/tags" if '/v1' in base_url else f"{base_url}/api/tags"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return [{'id': m['name'], 'name': m['name']} for m in data.get('models', [])]
    except Exception:
        return []

def fetch_generic_models(api_url: str, api_key: Optional[str], provider_name: str = "") -> List[Dict]:
    """Fetch models from generic OpenAI-compatible endpoint.
    
    Tries multiple endpoints in order:
    1. /models (standard OpenAI)
    2. /v1/models (if not already in base URL)
    3. Provider-specific endpoints
    """
    headers = {'Accept': 'application/json'}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    # Try different endpoint variations
    endpoints_to_try = [
        f"{api_url.rstrip('/')}/models",
    ]
    
    # Add provider-specific endpoints
    provider_lower = provider_name.lower() if provider_name else ""
    if 'google' in provider_lower or 'gemini' in provider_lower:
        # Google AI Studio uses a different format
        endpoints_to_try.insert(0, f"{api_url.rstrip('/')}/models/list")
    
    for url in endpoints_to_try:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                models_data = data.get('data', []) or data.get('models', [])
                return models_data
        except Exception as e:
            # Try next endpoint
            continue
    
    return []

def is_free_model(model: Dict, provider: str) -> bool:
    """Check if a model is free tier."""
    model_id = model.get('id', '').lower()
    
    # Check OpenRouter-specific free markers
    if provider == 'openrouter':
        pricing = model.get('pricing', {})
        if pricing:
            prompt_price = float(pricing.get('prompt', '0') or '0')
            completion_price = float(pricing.get('completion', '0') or '0')
            if prompt_price == 0 and completion_price == 0:
                return True
    
    # Check for :free suffix (NVIDIA OpenRouter)
    if ':free' in model_id or '/free' in model_id:
        return True
    
    # Check common free model patterns
    free_patterns = ['free', 'gemma-2b', 'tiny', 'nano']
    for pattern in free_patterns:
        if pattern in model_id:
            return True
    
    return False

def list_providers_main(args=None) -> None:
    """Main function to list providers and models."""
    config_path = Path(args.config) if args and args.config else DEFAULT_CONFIG
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    providers = config.get('providers', {})
    
    print("\n" + "="*80)
    print("🔧 HERMES AGENT - UNIFIED PROVIDER & MODEL LIST")
    print("="*80)
    print(f"Config: {config_path}")
    print(f"Total Providers: {len(providers)}")
    print("="*80 + "\n")
    
    # Track if we should update config
    update_config = args and getattr(args, 'update_config', False)
    config_changed = False
    
    for provider_name, provider_config in providers.items():
        # Filter by provider name if specified
        if args.provider and provider_name.lower() != args.provider.lower():
            continue
        
        api_url = provider_config.get('api', '')
        api_key = get_env_var(provider_config.get('api_key', ''))
        configured_models = provider_config.get('models', [])
        default_model = provider_config.get('default_model', 'N/A')
        
        print(f"\n{'─'*80}")
        print(f"📦 Provider: {provider_name.upper()}")
        print(f"   API URL: {api_url}")
        print(f"   Default Model: {default_model}")
        print(f"   Configured Models: {len(configured_models)}")
        
        if configured_models:
            print(f"   Models:")
            for model in configured_models[:5]:
                print(f"     • {model}")
            if len(configured_models) > 5:
                print(f"     ... and {len(configured_models) - 5} more")
        
        # Try to fetch live models from API
        print(f"\n 🔄 Fetching available models from API...")
        
        live_models = []
        fetch_error = None
        provider_lower = provider_name.lower()
        
        if 'openrouter' in provider_lower:
            live_models = fetch_openrouter_models(api_key)
        elif 'ollama' in provider_lower:
            live_models = fetch_ollama_models(api_url)
        elif api_url:
            live_models = fetch_generic_models(api_url, api_key, provider_name)
        
        if live_models:
            print(f"   ✅ Found {len(live_models)} models from API")
            
            # Show free models
            free_models = [m for m in live_models if is_free_model(m, provider_lower)]
            if free_models:
                print(f"\n   🆓 FREE TIER MODELS ({len(free_models)}):")
                for model in free_models[:10]:
                    model_id = model.get('id', 'unknown')
                    print(f"     • {model_id}")
                if len(free_models) > 10:
                    print(f"     ... and {len(free_models) - 10} more")
            
            # Show all models if not free_only
            if not args.free_only:
                print(f"\n   📋 ALL AVAILABLE MODELS ({len(live_models)}):")
                for model in live_models[:15]:
                    model_id = model.get('id', 'unknown')
                    is_free = is_free_model(model, provider_lower)
                    free_tag = " 🆓" if is_free else ""
                    print(f"     • {model_id}{free_tag}")
                if len(live_models) > 15:
                    print(f"     ... and {len(live_models) - 15} more")
        else:
            # Provide better diagnostics
            print(f"   ⚠️  Could not fetch models from API")
            if not api_key and 'key' in provider_config.get('api_key', '').lower():
                print(f"      💡 Hint: API key may be required but not configured")
            if 'localhost' in api_url or '127.0.0.1' in api_url:
                print(f"      💡 Hint: Local endpoint may not be running")
            print(f"      Using configured models instead")
        
        # Update config if requested and we have live models
        if update_config and live_models:
            model_ids = [m.get('id', '') for m in live_models if m.get('id')]
            if model_ids:
                provider_config['models'] = model_ids
                config_changed = True
                print(f"\n   ✅ Updated config with {len(model_ids)} discovered models")
        
        print()
    
    # Save config if updated
    if update_config and config_changed:
        print("\n💾 Saving updated configuration...")
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        print("✅ Configuration saved!")
    elif update_config and not config_changed:
        print("\n⚠️  No updates made (no new models discovered)")

def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='List Hermes providers and models')
    parser.add_argument('--provider', '-p', type=str, help='Filter by provider name')
    parser.add_argument('--free-only', '-f', action='store_true', help='Show only free tier models')
    parser.add_argument('--config', type=str, default=str(DEFAULT_CONFIG), help='Path to config.yaml')
    parser.add_argument('--update-config', action='store_true', help='Update config.yaml with discovered models')
    
    args = parser.parse_args()
    list_providers_main(args)

if __name__ == '__main__':
    main()
