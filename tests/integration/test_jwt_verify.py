#!/usr/bin/env python3
"""Test JWT verification with your token."""

import base64
import contextlib
import json
import os
import sys

import jwt

# Your JWT token from the request
token = "eyJhbGciOiJIUzI1NiIsImtpZCI6IjhHb2w2WEVpdGZHTHJub2wiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3prc3NhenFod2NldHNuYml1cWlrLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJiOTI4NGQ0Ny03MmI1LTQ5NjAtYTE3Ny0wNzg4ZmM0YjA4MDkiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzUxMTIwNjA1LCJpYXQiOjE3NTExMTcwMDUsImVtYWlsIjoid3Jhc3RsZXlAZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJnb29nbGUiLCJwcm92aWRlcnMiOlsiZ29vZ2xlIl19LCJ1c2VyX21ldGFkYXRhIjp7ImF2YXRhcl91cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NJQXpRSnV1RmZBc2lycjR6RHotbzA2LW5QYkg5bWM3ay1kall1SDcwMms0eGkzcEZxbz1zOTYtYyIsImVtYWlsIjoid3Jhc3RsZXlAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6IldpbGxpYW0gQXN0bGV5IiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwibmFtZSI6IldpbGxpYW0gQXN0bGV5IiwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jSUF6UUp1dUZmQXNpcnI0ekR6LW8wNi1uUGJIOW1jN2stZGpZdUg3MDJrNHhpM3BGcW89czk2LWMiLCJwcm92aWRlcl9pZCI6IjExMzkyMDYyNDQ0MTk3OTE2ODE2MiIsInN1YiI6IjExMzkyMDYyNDQ0MTk3OTE2ODE2MiJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6Im9hdXRoIiwidGltZXN0YW1wIjoxNzUxMDY0MzQ2fV0sInNlc3Npb25faWQiOiI4YjIwZmM4OC0wNmYwLTRmMWEtODE5Zi1lMjU1OTBjNTEzNTQiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.fw0ZHcGzG8BANoCLGz3V2_TA_DbygbT0Fgf9jJLt7FA"

# Load environment
sys.path.insert(0, "packages/haive-dataflow/src")
os.environ["SUPABASE_JWT_SECRET"] = (
    "J89XqGf7hDkKejOK1n02TKVT78TtncD3gP0TH68N4AV1H87viAt9EhQxVp0mfUxkBNHowVCng2okkmPHYZpiKA=="
)


# Decode without verification first
parts = token.split(".")
header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))


# Try to verify

# Method 1: Direct verification
try:
    secret = os.environ["SUPABASE_JWT_SECRET"]
    verified = jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
except Exception:
    pass

# Method 2: Using the Supabase auth class
try:
    from haive.dataflow.auth.supabase import SupabaseAuth

    auth = SupabaseAuth()
    result = auth.verify_token(token)
    if result:
        pass
    else:
        pass
except Exception:
    pass

# Method 3: Try without audience check
with contextlib.suppress(Exception):
    verified = jwt.decode(
        token, secret, algorithms=["HS256"], options={"verify_aud": False}
    )
