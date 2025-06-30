#!/usr/bin/env python3
"""Debug authentication issues with Supabase JWT tokens"""

import base64
import json
import os
import sys

import jwt


def decode_jwt_without_verification(token):
    """Decode JWT without verification to inspect contents"""
    parts = token.split('.')
    if len(parts) != 3:
        print("Invalid JWT format")
        return None
    
    # Decode header
    header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
    
    # Decode payload
    payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
    
    return header, payload

def main():
    print("=== Supabase JWT Debug Tool ===\n")
    
    # Check environment variables
    print("1. Environment Variables:")
    env_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL", "NOT SET"),
        "SUPABASE_JWT_SECRET": os.getenv("SUPABASE_JWT_SECRET", "NOT SET"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", "NOT SET"),
        "SUPABASE_SERVICE_KEY": os.getenv("SUPABASE_SERVICE_KEY", "NOT SET")
    }
    
    for key, value in env_vars.items():
        if value != "NOT SET" and key.endswith("KEY") or key.endswith("SECRET"):
            # Show only first and last 3 chars for security
            display_value = f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "***"
        else:
            display_value = value
        print(f"  {key}: {display_value}")
    
    print("\n2. JWT Token Analysis:")
    
    # Get token from command line or prompt
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("\nPaste your JWT token (or press Enter to skip):")
        token = input().strip()
    
    if token:
        try:
            header, payload = decode_jwt_without_verification(token)
            print("\n  Header:", json.dumps(header, indent=2))
            print("\n  Payload:", json.dumps(payload, indent=2))
            
            # Check if we can verify with the secret
            jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
            if jwt_secret:
                print("\n3. Verification attempt:")
                try:
                    verified = jwt.decode(
                        token,
                        jwt_secret,
                        algorithms=["HS256"],
                        audience="authenticated"
                    )
                    print("  ✓ Token verified successfully!")
                except Exception as e:
                    print(f"  ✗ Verification failed: {e}")
            else:
                print("\n3. Cannot verify - SUPABASE_JWT_SECRET not set")
                print("\nTo fix authentication:")
                print("1. Get your JWT secret from Supabase dashboard:")
                print("   - Go to Project Settings > API")
                print("   - Copy the JWT Secret")
                print("2. Set the environment variable:")
                print("   export SUPABASE_JWT_SECRET='your-secret-here'")
    else:
        print("  No token provided")

if __name__ == "__main__":
    main()