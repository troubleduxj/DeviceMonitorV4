import asyncio
import os
import asyncpg
from dotenv import load_dotenv

async def fix_schema():
    # Try loading .env.dev first, then .env
    if os.path.exists("app/.env.dev"):
        print("Loading app/.env.dev")
        load_dotenv("app/.env.dev")
    elif os.path.exists("app/.env"):
        print("Loading app/.env")
        load_dotenv("app/.env")
    elif os.path.exists(".env"):
        print("Loading .env")
        load_dotenv(".env")
    else:
        print("No .env file found, using defaults")
    
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "123456")
    database = os.getenv("POSTGRES_DATABASE", "device_monitor")
    
    print(f"Connecting to {user}@{host}:{port}/{database}")
    
    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port,
            ssl='disable'
        )
        print("Connected successfully.")
        
        # Check and add started_at
        print("Checking 'started_at' column...")
        col_exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 't_ai_models' AND column_name = 'started_at'
            )
            """
        )
        if not col_exists:
            print("Adding 'started_at' column...")
            await conn.execute('ALTER TABLE "t_ai_models" ADD COLUMN "started_at" TIMESTAMPTZ')
            print("Added 'started_at'.")
        else:
            print("'started_at' already exists.")

        # Check and add finished_at
        print("Checking 'finished_at' column...")
        col_exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 't_ai_models' AND column_name = 'finished_at'
            )
            """
        )
        if not col_exists:
            print("Adding 'finished_at' column...")
            await conn.execute('ALTER TABLE "t_ai_models" ADD COLUMN "finished_at" TIMESTAMPTZ')
            print("Added 'finished_at'.")
        else:
            print("'finished_at' already exists.")
            
        # Check and add task_id (often missing in updates)
        print("Checking 'task_id' column...")
        col_exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 't_ai_models' AND column_name = 'task_id'
            )
            """
        )
        if not col_exists:
            print("Adding 'task_id' column...")
            await conn.execute('ALTER TABLE "t_ai_models" ADD COLUMN "task_id" VARCHAR(64)')
            print("Added 'task_id'.")
        else:
            print("'task_id' already exists.")

        # Check and add error_log
        print("Checking 'error_log' column...")
        col_exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 't_ai_models' AND column_name = 'error_log'
            )
            """
        )
        if not col_exists:
            print("Adding 'error_log' column...")
            await conn.execute('ALTER TABLE "t_ai_models" ADD COLUMN "error_log" TEXT')
            print("Added 'error_log'.")
        else:
            print("'error_log' already exists.")
            
        # Check and add resource_usage
        print("Checking 'resource_usage' column...")
        col_exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 't_ai_models' AND column_name = 'resource_usage'
            )
            """
        )
        if not col_exists:
            print("Adding 'resource_usage' column...")
            await conn.execute('ALTER TABLE "t_ai_models" ADD COLUMN "resource_usage" JSONB DEFAULT \'{}\'::jsonb')
            print("Added 'resource_usage'.")
        else:
            print("'resource_usage' already exists.")

        await conn.close()
        print("Schema update completed.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_schema())
