"""
Test Data Generator for Duty System
Creates realistic test batches covering all 4 SPR categories
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.constants import CACHE_DB_PATH


class TestDataGenerator:
    """Generates realistic test data for the duty system"""

    def __init__(self):
        self.conn = sqlite3.connect(CACHE_DB_PATH)
        self.cursor = self.conn.cursor()
        self.user = "admin"

        # Load duty rates from settings
        self.load_settings()

        # Load container configurations
        self.load_containers()

    def load_settings(self):
        """Load duty rates from settings table"""
        self.cursor.execute('''
            SELECT
                spr_draught_low,
                spr_draught_standard,
                spr_non_draught_standard,
                rate_full_8_5_to_22
            FROM settings
            WHERE id = 1
        ''')

        row = self.cursor.fetchone()
        if not row:
            print("ERROR: Settings not configured. Please run migration first.")
            sys.exit(1)

        self.spr_draught_low = row[0]
        self.spr_draught_std = row[1]
        self.spr_non_draught = row[2]
        self.rate_full = row[3]

        print(f"Loaded duty rates:")
        print(f"  SPR Draught Low: £{self.spr_draught_low:.2f}/LPA")
        print(f"  SPR Draught Std: £{self.spr_draught_std:.2f}/LPA")
        print(f"  SPR Non-Draught: £{self.spr_non_draught:.2f}/LPA")
        print(f"  Full Rate 8.5-22%: £{self.rate_full:.2f}/LPA\n")

    def load_containers(self):
        """Load container configurations"""
        self.cursor.execute('''
            SELECT name, duty_paid_volume, is_draught_eligible
            FROM settings_containers
            WHERE active = 1
        ''')

        self.containers = {}
        for row in self.cursor.fetchall():
            name, duty_vol, is_draught = row
            self.containers[name] = {
                'duty_volume': duty_vol,
                'is_draught': is_draught == 1
            }

        print(f"Loaded {len(self.containers)} container types")

    def calculate_duty(self, abv, is_draught):
        """Determine SPR category and duty rate"""
        if abv >= 8.5:
            spr_category = "no_spr"
            duty_rate = self.rate_full
        elif abv < 3.5 and is_draught:
            spr_category = "draught_low"
            duty_rate = self.spr_draught_low
        elif 3.5 <= abv < 8.5 and is_draught:
            spr_category = "draught_standard"
            duty_rate = self.spr_draught_std
        elif 3.5 <= abv < 8.5 and not is_draught:
            spr_category = "non_draught_standard"
            duty_rate = self.spr_non_draught
        else:
            raise ValueError(f"Cannot determine duty category for ABV {abv}, draught={is_draught}")

        return spr_category, duty_rate

    def create_batch(self, batch_data):
        """Create a batch and packaging lines"""
        batch_id = batch_data['batch_id']
        gyle = batch_data['gyle_number']
        name = batch_data['beer_name']
        style = batch_data['style']
        abv = batch_data['abv']
        packaging_date = batch_data['packaging_date']
        packaging_lines = batch_data['packaging']

        print(f"\nCreating Batch: {gyle} - {name} ({style}, {abv}% ABV)")

        # Insert batch record
        now = datetime.now().isoformat()

        self.cursor.execute('''
            INSERT INTO batches (
                batch_id,
                gyle_number,
                beer_name,
                style,
                measured_abv,
                status,
                brew_date,
                created_date,
                created_by,
                last_modified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (batch_id, gyle, name, style, abv, 'Packaged',
              packaging_date, now, self.user, now))

        # Create packaging lines
        for line in packaging_lines:
            container_type = line['container']
            quantity = line['quantity']

            if container_type not in self.containers:
                print(f"  WARNING: Container '{container_type}' not found, skipping")
                continue

            container_info = self.containers[container_type]
            duty_volume_per_unit = container_info['duty_volume']
            is_draught = container_info['is_draught']

            # Calculate volumes
            total_duty_volume = duty_volume_per_unit * quantity
            pure_alcohol_litres = total_duty_volume * (abv / 100)

            # Determine SPR category and rate
            spr_category, duty_rate = self.calculate_duty(abv, is_draught)

            # Calculate duty payable
            duty_payable = pure_alcohol_litres * duty_rate

            # Insert packaging line
            self.cursor.execute('''
                INSERT INTO batch_packaging_lines (
                    batch_id,
                    packaging_date,
                    container_type,
                    quantity,
                    container_actual_size,
                    container_duty_volume,
                    total_duty_volume,
                    batch_abv,
                    pure_alcohol_litres,
                    spr_category,
                    spr_rate_applied,
                    full_duty_rate,
                    effective_duty_rate,
                    duty_payable,
                    is_draught_eligible
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (batch_id, packaging_date, container_type, quantity,
                  duty_volume_per_unit, duty_volume_per_unit, total_duty_volume,
                  abv, pure_alcohol_litres, spr_category,
                  duty_rate, self.rate_full, duty_rate, duty_payable,
                  1 if is_draught else 0))

            print(f"  ✓ {quantity}x {container_type}: {total_duty_volume:.2f}L, {pure_alcohol_litres:.2f} LPA, £{duty_payable:.2f} ({spr_category})")

    def create_spoilt_beer(self, spoilt_data):
        """Create spoilt beer record"""
        print(f"\n Creating Spoilt Beer Record: {spoilt_data['quantity']}x {spoilt_data['container']}")

        container_type = spoilt_data['container']
        quantity = spoilt_data['quantity']
        abv = spoilt_data['abv']
        duty_month = spoilt_data['duty_month']
        date_discovered = spoilt_data['date_discovered']
        reason = spoilt_data['reason']

        if container_type not in self.containers:
            print(f"  WARNING: Container '{container_type}' not found, skipping")
            return

        container_info = self.containers[container_type]
        duty_volume_per_unit = container_info['duty_volume']
        is_draught = container_info['is_draught']

        # Calculate volumes
        total_volume = duty_volume_per_unit * quantity
        pure_alcohol_litres = total_volume * (abv / 100)

        # Determine SPR category and rate (from original packaging)
        spr_category, duty_rate = self.calculate_duty(abv, is_draught)

        # Calculate duty to reclaim
        duty_to_reclaim = pure_alcohol_litres * duty_rate

        now = datetime.now().isoformat()

        self.cursor.execute('''
            INSERT INTO spoilt_beer (
                batch_id,
                gyle_number,
                date_discovered,
                duty_month,
                status,
                container_type,
                quantity,
                total_volume,
                duty_paid_volume,
                pure_alcohol_litres,
                spr_category,
                original_duty_rate,
                duty_to_reclaim,
                reason_category,
                reason_notes,
                recorded_by,
                recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (None, None, date_discovered, duty_month, 'approved',
              container_type, quantity, total_volume, total_volume,
              pure_alcohol_litres, spr_category, duty_rate, duty_to_reclaim,
              reason, f"Test data: {reason}", self.user, now))

        print(f"  ✓ Spoilt: {total_volume:.2f}L, Duty Reclaim: £{duty_to_reclaim:.2f}")

    def generate_all(self):
        """Generate complete test dataset"""
        print("\n" + "=" * 70)
        print("GENERATING TEST DATA FOR DUTY SYSTEM")
        print("=" * 70)

        # Define test batches covering all 4 SPR categories
        base_date = datetime.now() - timedelta(days=15)

        test_batches = [
            # Batch 1: Category 1 - Draught <3.5% ABV (SPR Low)
            {
                'batch_id': str(uuid.uuid4()),
                'gyle_number': 'TEST001',
                'beer_name': 'Easy Session IPA',
                'style': 'Session IPA',
                'abv': 3.2,
                'packaging_date': (base_date + timedelta(days=0)).strftime('%Y-%m-%d'),
                'packaging': [
                    {'container': 'Firkin', 'quantity': 10},
                    {'container': '30L Keg', 'quantity': 5},
                ]
            },

            # Batch 2: Category 2 - Draught 3.5-8.4% ABV (SPR Standard)
            {
                'batch_id': str(uuid.uuid4()),
                'gyle_number': 'TEST002',
                'beer_name': 'Classic Bitter',
                'style': 'English Bitter',
                'abv': 4.5,
                'packaging_date': (base_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                'packaging': [
                    {'container': 'Firkin', 'quantity': 15},
                    {'container': 'Pin', 'quantity': 8},
                ]
            },

            # Batch 3: Category 3 - Non-Draught 3.5-8.4% ABV (SPR Standard)
            {
                'batch_id': str(uuid.uuid4()),
                'gyle_number': 'TEST003',
                'beer_name': 'West Coast IPA',
                'style': 'American IPA',
                'abv': 5.8,
                'packaging_date': (base_date + timedelta(days=7)).strftime('%Y-%m-%d'),
                'packaging': [
                    {'container': 'Bottle 500ml', 'quantity': 200},
                    {'container': 'Bottle 330ml', 'quantity': 150},
                ]
            },

            # Batch 4: Category 4 - High ABV 8.5-22% (No SPR)
            {
                'batch_id': str(uuid.uuid4()),
                'gyle_number': 'TEST004',
                'beer_name': 'Imperial Russian Stout',
                'style': 'Imperial Stout',
                'abv': 9.5,
                'packaging_date': (base_date + timedelta(days=10)).strftime('%Y-%m-%d'),
                'packaging': [
                    {'container': 'Bottle 750ml', 'quantity': 100},
                    {'container': 'Bottle 330ml', 'quantity': 50},
                ]
            },
        ]

        # Create all batches
        for batch in test_batches:
            self.create_batch(batch)

        # Create some spoilt beer records for testing refunds
        current_month = datetime.now().strftime('%Y-%m')

        spoilt_records = [
            {
                'container': 'Firkin',
                'quantity': 2,
                'abv': 4.5,
                'duty_month': current_month,
                'date_discovered': datetime.now().strftime('%Y-%m-%d'),
                'reason': 'Infection/Contamination'
            },
            {
                'container': 'Bottle 500ml',
                'quantity': 24,
                'abv': 5.8,
                'duty_month': current_month,
                'date_discovered': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'reason': 'Package Defect/Leakage'
            },
        ]

        for spoilt in spoilt_records:
            self.create_spoilt_beer(spoilt)

        # Commit all changes
        self.conn.commit()

        print("\n" + "=" * 70)
        print("✅ TEST DATA GENERATION COMPLETE!")
        print("=" * 70)
        print("\nGenerated:")
        print(f"  • {len(test_batches)} test batches covering all 4 SPR categories")
        print(f"  • {sum(len(b['packaging']) for b in test_batches)} packaging lines with duty calculations")
        print(f"  • {len(spoilt_records)} spoilt beer records for refund testing")
        print("\nYou can now:")
        print("  1. View batches in the Production module")
        print("  2. View duty returns in the Duty module")
        print("  3. View spoilt beer in Products > Spoilt Beer tab")
        print("  4. View reports in the Reports module")
        print("  5. Adjust settings in the Settings module")
        print("=" * 70)

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main execution"""
    print("\n⚠️  WARNING: This will add test data to your database.")
    print("   Test batches will have gyle numbers: TEST001, TEST002, TEST003, TEST004")
    print("   You can identify and delete them later if needed.\n")

    response = input("Continue with test data generation? (yes/no): ")
    if response.lower() != 'yes':
        print("\nTest data generation cancelled.")
        return

    generator = TestDataGenerator()
    try:
        generator.generate_all()
    finally:
        generator.close()


if __name__ == "__main__":
    main()
