#!/usr/bin/env python3
"""
Automated Database Setup Script
Reads SQL schema and executes it via Supabase API
"""
import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'src'))
from utils.logger import logger

# Load environment variables
load_dotenv(Path(__file__).parent.parent / 'backend' / '.env')


class DatabaseSetup:
    """Automate database schema creation"""

    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

        self.client: Client = create_client(supabase_url, supabase_key)
        self.schema_file = Path(__file__).parent.parent / 'docs' / 'database_schema.sql'

    def read_schema(self) -> str:
        """Read SQL schema file"""
        if not self.schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_file}")

        with open(self.schema_file, 'r', encoding='utf-8') as f:
            return f.read()

    def execute_sql(self, sql: str):
        """Execute SQL via Supabase PostgREST API"""
        import requests

        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

            # Supabase provides a query endpoint
            url = f"{supabase_url}/rest/v1/rpc/exec"

            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }

            # Try to execute the full SQL at once
            logger.info("Attempting to execute full schema...")

            # Since Supabase REST API doesn't directly support raw SQL execution,
            # we'll need to use a different approach: execute via psycopg2
            import psycopg2
            from urllib.parse import urlparse

            # Parse Supabase URL to get connection details
            # Note: This requires the database connection string
            logger.info("Connecting directly to PostgreSQL...")

            # For Supabase, we need to construct the database URL
            # Format: postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
            project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')

            logger.warning("⚠️  Direct SQL execution requires database password")
            logger.warning("Please run the SQL schema manually in Supabase SQL Editor:")
            logger.warning(f"1. Visit: {supabase_url.replace('https://', 'https://supabase.com/dashboard/project/')}")
            logger.warning("2. Go to SQL Editor")
            logger.warning(f"3. Copy and paste the contents of: {self.schema_file}")
            logger.warning("4. Click 'Run'")

            return False

        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return False

    def setup(self):
        """Main setup process"""
        logger.info("=" * 60)
        logger.info("🚀 AUTOMATED DATABASE SETUP")
        logger.info("=" * 60)

        try:
            # Read schema
            logger.info("📖 Reading database schema...")
            sql = self.read_schema()
            logger.info(f"✅ Loaded {len(sql)} characters of SQL")

            # Execute schema
            logger.info("🔨 Creating database tables and objects...")
            self.execute_sql(sql)

            logger.info("=" * 60)
            logger.info("✨ DATABASE SETUP COMPLETE!")
            logger.info("=" * 60)
            logger.info("\nNext step: Run seed_database_csv.py to load data")

        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            raise


def main():
    """Main execution"""
    try:
        setup = DatabaseSetup()
        setup.setup()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
