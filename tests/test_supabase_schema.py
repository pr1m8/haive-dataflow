# check_schema.py
import asyncio
import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


async def check_schema():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_ANON_KEY"))

    client = create_client(url, key)

    # List tables in public schema
    response = await client.rpc(
        "pg_catalog.pg_tables", {"schemaname": "public"}
    ).execute()

    for _table in response.data:
        pass

    # Try to list tables in user_data schema (if exists)
    response = await client.rpc(
        "pg_catalog.pg_tables", {"schemaname": "user_data"}
    ).execute()

    for _table in response.data:
        pass

    # Check RLS policies
    response = await client.from_("pg_catalog.pg_policies").select("*").execute()

    for _policy in response.data:
        pass


asyncio.run(check_schema())
