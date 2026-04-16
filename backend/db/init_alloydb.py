import asyncio
import os
import asyncpg
from google.cloud.alloydb.connector import Connector

# Configuration
PROJECT_ID = "nirman-project-493414"
REGION = "asia-south1"
CLUSTER = "sarathi-cluster"
INSTANCE = "sarathi-primary"
DB_NAME = "sarathi"
USER = "postgres"
PASSWORD = "TempPass789!@#" # The password we just reset
INSTANCE_URI = f"projects/{PROJECT_ID}/locations/{REGION}/clusters/{CLUSTER}/instances/{INSTANCE}"

async def run_sql_file(conn, file_path):
    print(f"📖 Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split by semicolon but handle triggers/functions (simplistic split)
    # Actually, for schema.sql, running the whole block is often better if the driver supports it
    print(f"🚀 Executing commands from {file_path}...")
    await conn.execute(sql)
    print(f"✅ Finished {file_path}")

async def initialize():
    connector = Connector()

    async def getconn():
        conn = await connector.connect_async(
            INSTANCE_URI,
            "asyncpg",
            user=USER,
            password=PASSWORD,
            db="postgres", # Initially connect to default postgres DB
            enable_iam_auth=False
        )
        return conn

    print("🔌 Connecting to AlloyDB (postgres database)...")
    conn = await getconn()
    
    try:
        # 1. Create database if not exists
        print(f"📦 Creating database '{DB_NAME}' if not exists...")
        # Note: CREATE DATABASE cannot run in a transaction block
        try:
            await conn.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✅ Database '{DB_NAME}' created.")
        except asyncpg.DuplicateDatabaseError:
            print(f"ℹ️ Database '{DB_NAME}' already exists.")
    finally:
        await conn.close()

    # 2. Connect to the new database to run schema and seed
    print(f"🔌 Connecting to AlloyDB ('{DB_NAME}' database)...")
    conn = await connector.connect_async(
        INSTANCE_URI,
        "asyncpg",
        user=USER,
        password=PASSWORD,
        db=DB_NAME,
        enable_iam_auth=False
    )

    try:
        # 3. Create IAM user mapping in database
        IAM_USER = "dubeybishal70@gmail.com"
        print(f"👤 Creating IAM user mapping for {IAM_USER}...")
        try:
            await conn.execute(f'CREATE USER "{IAM_USER}" WITH LOGIN;')
            await conn.execute(f'GRANT alloydbiamuser TO "{IAM_USER}";')
            print(f"✅ IAM user mapping created.")
        except Exception as e:
            print(f"ℹ️ IAM user mapping already exists or failed: {e}")

        # 4. Run schema
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        await run_sql_file(conn, schema_path)

        # 5. Run seed
        seed_path = os.path.join(os.path.dirname(__file__), "seed.sql")
        if os.path.exists(seed_path):
            await run_sql_file(conn, seed_path)
        else:
            print("⚠️ seed.sql not found, skipping.")

    finally:
        await conn.close()
        await connector.close_async()

if __name__ == "__main__":
    asyncio.run(initialize())
