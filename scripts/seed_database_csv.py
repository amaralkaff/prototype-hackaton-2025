import csv
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'src'))

from utils.logger import logger

# Load environment variables
load_dotenv(Path(__file__).parent.parent / 'backend' / '.env')


class DatabaseSeederCSV:
    """Seed Supabase database with CSV data"""

    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")

        self.client: Client = create_client(supabase_url, supabase_key)
        self.data_dir = Path(__file__).parent.parent / 'data' / 'seed'

    def load_csv_file(self, filename: str) -> list:
        """Load CSV data from file"""
        filepath = self.data_dir / filename

        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return []

        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert empty strings to None
                row = {k: (v if v != '' else None) for k, v in row.items()}
                # Convert boolean strings
                for key in ['has_bank_account', 'keeps_financial_records']:
                    if key in row and row[key] is not None:
                        row[key] = row[key].lower() == 'true'
                # Convert numeric strings
                for key in ['age', 'num_dependents', 'financial_literacy_score', 'loan_term_weeks', 'file_size_kb', 'days_overdue']:
                    if key in row and row[key] is not None:
                        row[key] = int(float(row[key]))
                for key in ['claimed_monthly_income', 'years_in_business', 'loan_amount', 'interest_rate', 'initial_credit_score', 'expected_amount', 'paid_amount']:
                    if key in row and row[key] is not None:
                        row[key] = float(row[key])

                data.append(row)

        logger.info(f"Loaded {len(data)} records from {filename}")
        return data

    def seed_borrowers(self):
        """Seed borrowers table"""
        logger.info("Seeding borrowers...")

        borrowers = self.load_csv_file('borrowers_seed.csv')

        if not borrowers:
            logger.warning("No borrower data found")
            return

        # Remove 'id' field
        for borrower in borrowers:
            borrower.pop('id', None)

        try:
            batch_size = 50
            for i in range(0, len(borrowers), batch_size):
                batch = borrowers[i:i + batch_size]
                response = self.client.table('borrowers').insert(batch).execute()
                logger.info(f"Inserted borrowers batch {i // batch_size + 1}")

            logger.info(f"✅ Successfully seeded {len(borrowers)} borrowers")

        except Exception as e:
            logger.error(f"Error seeding borrowers: {e}")
            raise

    def seed_loans(self):
        """Seed loans table"""
        logger.info("Seeding loans...")

        loans = self.load_csv_file('loans_seed.csv')

        if not loans:
            logger.warning("No loan data found")
            return

        # Get borrower ID mappings
        borrowers_response = self.client.table('borrowers').select('id, full_name').execute()
        borrowers = borrowers_response.data
        id_mapping = {i + 1: borrower['id'] for i, borrower in enumerate(borrowers)}

        # Update references
        for loan in loans:
            loan.pop('id', None)
            borrower_seq_id = int(loan['borrower_id'])
            loan['borrower_id'] = id_mapping.get(borrower_seq_id)
            loan.pop('repayment_profile', None)

        try:
            batch_size = 50
            for i in range(0, len(loans), batch_size):
                batch = loans[i:i + batch_size]
                response = self.client.table('loans').insert(batch).execute()
                logger.info(f"Inserted loans batch {i // batch_size + 1}")

            logger.info(f"✅ Successfully seeded {len(loans)} loans")

        except Exception as e:
            logger.error(f"Error seeding loans: {e}")
            raise

    def seed_repayments(self):
        """Seed repayments table"""
        logger.info("Seeding repayments...")

        repayments = self.load_csv_file('repayments_seed.csv')

        if not repayments:
            logger.warning("No repayment data found")
            return

        # Get loan ID mappings
        loans_response = self.client.table('loans').select('id, loan_amount').execute()
        loans = loans_response.data
        loan_id_mapping = {i + 1: loan['id'] for i, loan in enumerate(loans)}

        # Update references
        for repayment in repayments:
            repayment.pop('id', None)
            loan_seq_id = int(repayment['loan_id'])
            repayment['loan_id'] = loan_id_mapping.get(loan_seq_id)

        try:
            batch_size = 100
            for i in range(0, len(repayments), batch_size):
                batch = repayments[i:i + batch_size]
                response = self.client.table('repayments').insert(batch).execute()
                logger.info(f"Inserted repayments batch {i // batch_size + 1}")

            logger.info(f"✅ Successfully seeded {len(repayments)} repayments")

        except Exception as e:
            logger.error(f"Error seeding repayments: {e}")
            raise

    def seed_photos(self):
        """Seed photos table"""
        logger.info("Seeding photos...")

        photos = self.load_csv_file('photos_seed.csv')

        if not photos:
            logger.warning("No photo data found")
            return

        # Get borrower ID mappings
        borrowers_response = self.client.table('borrowers').select('id').execute()
        borrowers = borrowers_response.data
        borrower_id_mapping = {i + 1: borrower['id'] for i, borrower in enumerate(borrowers)}

        # Update references
        for photo in photos:
            photo.pop('id', None)
            borrower_seq_id = int(photo['borrower_id'])
            photo['borrower_id'] = borrower_id_mapping.get(borrower_seq_id)

        try:
            batch_size = 50
            for i in range(0, len(photos), batch_size):
                batch = photos[i:i + batch_size]
                response = self.client.table('photos').insert(batch).execute()
                logger.info(f"Inserted photos batch {i // batch_size + 1}")

            logger.info(f"✅ Successfully seeded {len(photos)} photos")

        except Exception as e:
            logger.error(f"Error seeding photos: {e}")
            raise

    def seed_field_notes(self):
        """Seed field_notes table"""
        logger.info("Seeding field notes...")

        field_notes = self.load_csv_file('field_notes_seed.csv')

        if not field_notes:
            logger.warning("No field notes data found")
            return

        # Get borrower ID mappings
        borrowers_response = self.client.table('borrowers').select('id').execute()
        borrowers = borrowers_response.data
        borrower_id_mapping = {i + 1: borrower['id'] for i, borrower in enumerate(borrowers)}

        # Update references
        for note in field_notes:
            note.pop('id', None)
            borrower_seq_id = int(note['borrower_id'])
            note['borrower_id'] = borrower_id_mapping.get(borrower_seq_id)

        try:
            batch_size = 50
            for i in range(0, len(field_notes), batch_size):
                batch = field_notes[i:i + batch_size]
                response = self.client.table('field_notes').insert(batch).execute()
                logger.info(f"Inserted field notes batch {i // batch_size + 1}")

            logger.info(f"✅ Successfully seeded {len(field_notes)} field notes")

        except Exception as e:
            logger.error(f"Error seeding field notes: {e}")
            raise

    def clear_all_data(self):
        """Clear all data from tables"""
        logger.warning("⚠️  Clearing all data from database...")

        tables = ['credit_assessments', 'field_notes', 'photos', 'repayments', 'loans', 'borrowers']

        for table in tables:
            try:
                response = self.client.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                logger.info(f"Cleared table: {table}")
            except Exception as e:
                logger.error(f"Error clearing {table}: {e}")

        logger.info("✅ All data cleared")

    def seed_all(self, clear_first: bool = False):
        """Seed all tables in correct order"""
        logger.info("=" * 60)
        logger.info("🌱 STARTING DATABASE SEEDING (CSV)")
        logger.info("=" * 60)

        if clear_first:
            confirm = input("⚠️  This will DELETE all existing data. Continue? (yes/no): ")
            if confirm.lower() == 'yes':
                self.clear_all_data()
            else:
                logger.info("Seeding cancelled")
                return

        try:
            self.seed_borrowers()
            self.seed_loans()
            self.seed_repayments()
            self.seed_photos()
            self.seed_field_notes()

            logger.info("=" * 60)
            logger.info("✨ DATABASE SEEDING COMPLETE!")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            raise


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Seed Amara AI database with CSV data')
    parser.add_argument('--clear', action='store_true', help='Clear all data before seeding')
    args = parser.parse_args()

    seeder = DatabaseSeederCSV()
    seeder.seed_all(clear_first=args.clear)


if __name__ == "__main__":
    main()
