import json
import random
from datetime import datetime, timedelta
from faker import Faker
from pathlib import Path

fake = Faker('id_ID')  # Indonesian locale


class DummyDataGenerator:
    """Generate realistic dummy data for Amara AI MVP"""

    def __init__(self, num_borrowers=75):
        self.num_borrowers = num_borrowers
        self.borrowers = []
        self.loans = []
        self.repayments = []
        self.photos = []
        self.field_notes = []

        # Business types with income ranges (in Rupiah)
        self.business_types = [
            ("Warung Kelontong (Small Shop)", 3000000, 5000000, 25),
            ("Warung Gorengan (Fried Snacks Stall)", 2000000, 3000000, 15),
            ("Jahit Pakaian (Tailoring)", 2500000, 4000000, 12),
            ("Jualan Sayur (Vegetable Vendor)", 1500000, 2500000, 10),
            ("Usaha Catering Rumahan (Home Catering)", 3000000, 6000000, 8),
            ("Salon Rumahan (Home Salon)", 2000000, 4000000, 7),
            ("Toko Pulsa & Aksesoris HP (Mobile Shop)", 2500000, 4000000, 6),
            ("Warung Nasi/Lauk Pauk (Food Stall)", 3000000, 5000000, 10),
            ("Industri Rumahan Kerupuk (Home Snack Industry)", 2000000, 3500000, 7),
        ]

        self.villages = ["Sukamaju", "Bojongsoang", "Cikalong", "Sindanglaya", "Margahayu", "Cipanas", "Rancaekek"]
        self.districts = ["Cianjur", "Bandung", "Tasikmalaya", "Garut", "Sumedang", "Majalengka"]

    def generate_all(self):
        """Generate all dummy data"""
        print("🚀 Starting dummy data generation...")
        self.generate_borrowers()
        self.generate_loans()
        self.generate_repayments()
        self.generate_photos_metadata()
        self.generate_field_notes()

        print(f"✅ Generated {len(self.borrowers)} borrowers")
        print(f"✅ Generated {len(self.loans)} loans")
        print(f"✅ Generated {len(self.repayments)} repayments")
        print(f"✅ Generated {len(self.photos)} photo records")
        print(f"✅ Generated {len(self.field_notes)} field notes")

        return {
            "borrowers": self.borrowers,
            "loans": self.loans,
            "repayments": self.repayments,
            "photos": self.photos,
            "field_notes": self.field_notes
        }

    def generate_borrowers(self):
        """Generate diverse borrower profiles"""
        print("👤 Generating borrowers...")

        # Calculate how many of each business type
        business_distribution = []
        for biz_type, min_inc, max_inc, percentage in self.business_types:
            count = int(self.num_borrowers * percentage / 100)
            business_distribution.extend([{
                "type": biz_type,
                "min_income": min_inc,
                "max_income": max_inc
            }] * count)

        # Fill remaining to reach exact num_borrowers
        while len(business_distribution) < self.num_borrowers:
            biz = random.choice(self.business_types)
            business_distribution.append({
                "type": biz[0],
                "min_income": biz[1],
                "max_income": biz[2]
            })

        for i, business in enumerate(business_distribution):
            age = random.randint(25, 55)
            has_bank = random.choice([True, False])
            keeps_records = random.choice([True, False])

            borrower = {
                "id": i + 1,
                "full_name": f"Ibu {fake.first_name_female()} {fake.last_name()}",
                "age": age,
                "gender": "Female",
                "village": f"Desa {random.choice(self.villages)}",
                "district": random.choice(self.districts),
                "province": "Jawa Barat",
                "business_type": business["type"],
                "business_description": self._generate_business_description(business["type"]),
                "claimed_monthly_income": random.randint(business["min_income"], business["max_income"]),
                "years_in_business": round(random.uniform(0.5, 15.0), 1),
                "marital_status": random.choice(["Menikah", "Janda", "Lajang"]),
                "num_dependents": random.randint(0, 5),
                "education_level": random.choice(["SD", "SMP", "SMA", "D3"]),
                "phone_number": f"08{random.randint(1000000000, 9999999999)}",
                "has_bank_account": has_bank,
                "keeps_financial_records": keeps_records,
                "financial_literacy_score": random.randint(20, 80),
            }

            self.borrowers.append(borrower)

    def _generate_business_description(self, business_type):
        """Generate contextual business descriptions"""
        descriptions = {
            "Warung Kelontong (Small Shop)": [
                "Jual kebutuhan sehari-hari seperti sabun, minyak goreng, gula, teh, rokok, snack anak-anak",
                "Warung kecil di depan rumah, jual sembako dan kebutuhan pokok warga sekitar",
                "Toko kelontong lengkap dengan produk rumah tangga dan makanan ringan"
            ],
            "Warung Gorengan (Fried Snacks Stall)": [
                "Jual gorengan seperti pisang goreng, tempe goreng, dan tahu isi setiap sore",
                "Warung gorengan buka dari sore sampai malam, pelanggan tetap banyak",
                "Produksi gorengan fresh setiap hari untuk dijual ke tetangga dan anak sekolah"
            ],
            "Jahit Pakaian (Tailoring)": [
                "Terima jahit baju, celana, dan rok untuk warga sekitar. Punya mesin jahit manual",
                "Usaha jahit pakaian custom dan perbaikan baju. Sudah punya pelanggan tetap",
                "Jahit baju rumah dan sekolah, kadang dapat pesanan seragam"
            ],
            "Jualan Sayur (Vegetable Vendor)": [
                "Jualan sayur keliling dari pagi sampai siang. Ambil sayur dari pasar grosir",
                "Jualan sayur mayur segar setiap hari, pelanggan ibu-ibu di komplek",
                "Dagang sayur di pasar pagi, pulang siang kalau sudah habis"
            ],
            "Usaha Catering Rumahan (Home Catering)": [
                "Terima pesanan nasi kotak untuk acara arisan, syukuran, atau ulang tahun",
                "Catering rumahan dengan menu nasi box dan nasi tumpeng untuk acara kecil-menengah",
                "Usaha katering spesial masakan Sunda, sering dapat pesanan event kantor"
            ],
            "Salon Rumahan (Home Salon)": [
                "Salon di rumah untuk potong rambut, creambath, dan cat rambut",
                "Salon kecil untuk wanita, layanan potong dan perawatan rambut dasar",
                "Usaha salon rumahan, buka setiap hari kecuali Minggu"
            ],
            "Toko Pulsa & Aksesoris HP (Mobile Shop)": [
                "Jual pulsa, paket data, dan aksesoris HP. Buka dari pagi sampai malam",
                "Counter HP untuk jual pulsa, token listrik, dan aksesoris handphone",
                "Toko pulsa lengkap dengan service HP ringan dan aksesoris"
            ],
            "Warung Nasi/Lauk Pauk (Food Stall)": [
                "Warung nasi dengan lauk pauk lengkap, buka dari siang sampai sore",
                "Jual nasi dengan berbagai lauk, pelanggan buruh pabrik dan ojek online",
                "Warung makan sederhana dengan menu nasi campur dan nasi goreng"
            ],
            "Industri Rumahan Kerupuk (Home Snack Industry)": [
                "Produksi kerupuk mentah untuk dijual ke warung-warung sekitar",
                "Industri rumah tangga bikin kerupuk dan keripik untuk dijual grosir",
                "Usaha kerupuk rumahan, produksi 10-20kg per minggu"
            ]
        }

        return random.choice(descriptions.get(business_type, ["Usaha mikro rumahan"]))

    def generate_loans(self):
        """Generate loan history with varied repayment patterns"""
        print("💰 Generating loans...")

        # Assign credit profiles: 40% good, 45% medium, 15% risky
        for i, borrower in enumerate(self.borrowers):
            if i < len(self.borrowers) * 0.4:
                profile = "good"
            elif i < len(self.borrowers) * 0.85:
                profile = "medium"
            else:
                profile = "risky"

            # Generate 1-3 loans per borrower
            num_loans = random.randint(1, 3)

            for j in range(num_loans):
                income = borrower["claimed_monthly_income"]
                loan_amount = random.randint(int(income * 0.5), int(income * 3.0))
                term_weeks = random.choice([16, 20, 24])
                disbursement = datetime.now() - timedelta(days=random.randint(30, 730))

                # Risk category based on profile
                if profile == "good":
                    risk = "low"
                    initial_score = random.uniform(75, 95)
                elif profile == "medium":
                    risk = "medium"
                    initial_score = random.uniform(55, 75)
                else:
                    risk = random.choice(["high", "very_high"])
                    initial_score = random.uniform(30, 55)

                loan = {
                    "id": len(self.loans) + 1,
                    "borrower_id": borrower["id"],
                    "loan_amount": loan_amount,
                    "loan_purpose": self._generate_loan_purpose(borrower["business_type"]),
                    "interest_rate": 2.5,
                    "loan_term_weeks": term_weeks,
                    "disbursement_date": disbursement.strftime("%Y-%m-%d"),
                    "maturity_date": (disbursement + timedelta(weeks=term_weeks)).strftime("%Y-%m-%d"),
                    "loan_status": random.choice(["active", "completed"]) if j < num_loans - 1 else "active",
                    "approval_status": "approved",
                    "initial_credit_score": round(initial_score, 2),
                    "risk_category": risk,
                    "repayment_profile": profile
                }

                self.loans.append(loan)

    def _generate_loan_purpose(self, business_type):
        """Generate contextual loan purposes"""
        purposes = {
            "Warung Kelontong": [
                "Tambah stok barang dagangan",
                "Beli kulkas untuk nyetok minuman dingin",
                "Renovasi warung dan tambah rak display"
            ],
            "Warung Gorengan": [
                "Beli kompor gas baru dan wajan besar",
                "Modal beli tepung dan minyak goreng",
                "Beli gerobak untuk jualan keliling"
            ],
            "Jahit Pakaian": [
                "Beli mesin jahit portable listrik",
                "Modal beli kain dan aksesoris jahit",
                "Renovasi ruang jahit supaya lebih luas"
            ],
            "Jualan Sayur": [
                "Modal beli sayuran dalam jumlah besar",
                "Beli gerobak dan timbangan digital",
                "Sewa lapak di pasar tradisional"
            ],
            "Catering": [
                "Beli peralatan masak dan panci besar",
                "Modal bahan baku untuk pesanan event",
                "Beli kulkas freezer untuk stok bahan"
            ]
        }

        for key in purposes:
            if key in business_type:
                return random.choice(purposes[key])

        return "Modal usaha dan pengembangan bisnis"

    def generate_repayments(self):
        """Generate repayment schedules based on borrower profile"""
        print("💳 Generating repayments...")

        for loan in self.loans:
            profile = loan['repayment_profile']
            term = loan['loan_term_weeks']
            weekly_amount = loan['loan_amount'] / term
            start_date = datetime.strptime(loan['disbursement_date'], "%Y-%m-%d")

            for week in range(term):
                due_date = start_date + timedelta(weeks=week + 1)

                # Skip future repayments
                if due_date > datetime.now():
                    continue

                # Good profile: 95% on time
                if profile == "good":
                    if random.random() < 0.95:
                        paid_date = due_date
                        days_overdue = 0
                    else:
                        days_overdue = random.randint(1, 3)
                        paid_date = due_date + timedelta(days=days_overdue)
                    payment_status = "paid"
                    paid_amount = weekly_amount

                # Medium profile: 75% on time, some delays
                elif profile == "medium":
                    if random.random() < 0.75:
                        paid_date = due_date
                        days_overdue = 0
                        payment_status = "paid"
                        paid_amount = weekly_amount
                    else:
                        days_overdue = random.randint(3, 10)
                        if random.random() < 0.8:
                            paid_date = due_date + timedelta(days=days_overdue)
                            payment_status = "late"
                            paid_amount = weekly_amount
                        else:
                            paid_date = None
                            payment_status = "partial"
                            paid_amount = weekly_amount * random.uniform(0.5, 0.9)

                # Risky profile: 50% on time, many issues
                else:
                    if random.random() < 0.5:
                        paid_date = due_date
                        days_overdue = 0
                        payment_status = "paid"
                        paid_amount = weekly_amount
                    else:
                        days_overdue = random.randint(7, 30)
                        if random.random() < 0.6:
                            paid_date = due_date + timedelta(days=days_overdue)
                            payment_status = "late"
                            paid_amount = weekly_amount * random.uniform(0.7, 1.0)
                        else:
                            paid_date = None
                            payment_status = "missed"
                            paid_amount = 0

                repayment = {
                    "id": len(self.repayments) + 1,
                    "loan_id": loan["id"],
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "paid_date": paid_date.strftime("%Y-%m-%d") if paid_date else None,
                    "expected_amount": round(weekly_amount, 2),
                    "paid_amount": round(paid_amount, 2),
                    "payment_status": payment_status,
                    "days_overdue": days_overdue
                }

                self.repayments.append(repayment)

    def generate_photos_metadata(self):
        """Generate photo metadata (actual images would be separate)"""
        print("📸 Generating photo metadata...")

        photo_types = [
            "business_exterior",
            "business_interior",
            "inventory",
            "house_exterior",
            "house_interior"
        ]

        for borrower in self.borrowers:
            # Each borrower has 2-4 photos
            num_photos = random.randint(2, 4)

            for j in range(num_photos):
                photo_type = random.choice(photo_types)

                photo = {
                    "id": len(self.photos) + 1,
                    "borrower_id": borrower["id"],
                    "photo_type": photo_type,
                    "photo_url": f"https://storage.supabase.co/borrower_{borrower['id']}_photo_{j + 1}.jpg",
                    "storage_path": f"borrowers/{borrower['id']}/photo_{j + 1}.jpg",
                    "file_size_kb": random.randint(200, 800),
                    "vision_analysis_status": "pending"
                }

                self.photos.append(photo)

    def generate_field_notes(self):
        """Generate realistic field agent narratives in Indonesian"""
        print("📝 Generating field notes...")

        for borrower in self.borrowers:
            # Each borrower has 1-2 field notes
            num_notes = random.randint(1, 2)

            for j in range(num_notes):
                note_type = random.choice(["initial_visit", "follow_up", "business_observation"])
                visit_date = datetime.now() - timedelta(days=random.randint(1, 90))

                note_text = self._generate_realistic_note(borrower, note_type)

                note = {
                    "id": len(self.field_notes) + 1,
                    "borrower_id": borrower["id"],
                    "loan_id": None,  # Will be linked if loan exists
                    "note_type": note_type,
                    "visit_date": visit_date.strftime("%Y-%m-%d"),
                    "note_text": note_text,
                    "field_agent_name": f"{random.choice(['Bapak', 'Ibu'])} {fake.name()}",
                    "nlp_analysis_status": "pending"
                }

                self.field_notes.append(note)

    def _generate_realistic_note(self, borrower, note_type):
        """Generate contextual field note narratives in Indonesian"""
        name = borrower["full_name"].split()[1]  # Get first name
        business = borrower["business_type"]
        income = borrower["claimed_monthly_income"]
        daily_income = income / 30

        templates = [
            f"Kunjungan ke usaha {business} milik {borrower['full_name']}. Usaha terletak di {borrower['village']}, {borrower['district']}. "
            f"Ibu {name} menceritakan penghasilan sekitar Rp {income:,.0f} per bulan atau sekitar Rp {daily_income:,.0f} per hari. "
            f"Sudah menjalankan usaha selama {borrower['years_in_business']} tahun. "
            f"{'Sudah punya buku catatan sederhana' if borrower['keeps_financial_records'] else 'Belum punya catatan keuangan yang rapi'}. "
            f"Sikap kooperatif dan terbuka menceritakan kondisi usaha. "
            f"{'Punya rekening bank' if borrower['has_bank_account'] else 'Belum punya rekening bank, transaksi masih cash'}. "
            f"Suami {'bekerja membantu usaha' if random.random() < 0.5 else 'bekerja di tempat lain'}. "
            f"Punya {borrower['num_dependents']} tanggungan anak.",

            f"Observasi bisnis {business}. Usaha terlihat {'ramai dengan pelanggan tetap' if random.random() < 0.6 else 'sepi tapi stabil'}. "
            f"Ibu {name} menjelaskan omzet harian sekitar Rp {daily_income:,.0f}, tergantung hari. "
            f"Kalau hari {'pasar atau weekend biasanya lebih ramai' if random.random() < 0.5 else 'kerja dan weekday lebih sepi'}. "
            f"Modal kerja harian sekitar Rp {income * 0.4:,.0f} untuk beli bahan baku dan stok. "
            f"{'Tempat usaha milik sendiri' if random.random() < 0.7 else 'Sewa tempat bulanan'}. "
            f"Peralatan usaha {'dalam kondisi baik' if random.random() < 0.6 else 'ada yang perlu diganti'}. "
            f"Rencana ingin {self._generate_loan_purpose(business).lower()}.",

            f"Pertemuan dengan Ibu {name} di rumah yang juga jadi tempat usaha {business}. "
            f"Rumah {'sederhana ukuran 6x8 meter, dinding tembok setengah bata' if random.random() < 0.6 else 'cukup layak dengan kondisi terawat'}. "
            f"Usaha sudah berjalan {borrower['years_in_business']} tahun dengan pelanggan {'tetap dan loyal' if random.random() < 0.5 else 'yang lumayan stabil'}. "
            f"Pendidikan {borrower['education_level']}, {'bisa baca tulis dan hitung dengan baik' if borrower['education_level'] != 'SD' else 'bisa baca tulis dasar'}. "
            f"Literasi keuangan {'cukup baik' if borrower['financial_literacy_score'] > 60 else 'masih perlu bimbingan'}. "
            f"Anak-anak masih {'sekolah semua' if borrower['num_dependents'] > 0 else 'tidak ada tanggungan sekolah'}. "
            f"{'Transparan dan kooperatif' if random.random() < 0.7 else 'Agak tertutup tapi mau bekerja sama'} saat wawancara."
        ]

        return random.choice(templates)

    def save_to_files(self, output_dir="data/seed"):
        """Save all generated data to JSON files"""
        print(f"💾 Saving data to {output_dir}...")

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Save each dataset
        with open(f"{output_dir}/borrowers_seed.json", "w", encoding='utf-8') as f:
            json.dump(self.borrowers, f, indent=2, ensure_ascii=False)

        with open(f"{output_dir}/loans_seed.json", "w", encoding='utf-8') as f:
            json.dump(self.loans, f, indent=2, ensure_ascii=False)

        with open(f"{output_dir}/repayments_seed.json", "w", encoding='utf-8') as f:
            json.dump(self.repayments, f, indent=2, ensure_ascii=False)

        with open(f"{output_dir}/photos_seed.json", "w", encoding='utf-8') as f:
            json.dump(self.photos, f, indent=2, ensure_ascii=False)

        with open(f"{output_dir}/field_notes_seed.json", "w", encoding='utf-8') as f:
            json.dump(self.field_notes, f, indent=2, ensure_ascii=False)

        print("✅ All data saved successfully!")


def main():
    """Main execution"""
    print("=" * 60)
    print("🎯 AMARA AI - DUMMY DATA GENERATOR")
    print("=" * 60)

    generator = DummyDataGenerator(num_borrowers=75)
    data = generator.generate_all()
    generator.save_to_files()

    print("\n" + "=" * 60)
    print("📊 GENERATION SUMMARY")
    print("=" * 60)
    print(f"Borrowers: {len(data['borrowers'])}")
    print(f"Loans: {len(data['loans'])}")
    print(f"Repayments: {len(data['repayments'])}")
    print(f"Photos: {len(data['photos'])}")
    print(f"Field Notes: {len(data['field_notes'])}")
    print("=" * 60)
    print("✨ Data generation complete!")


if __name__ == "__main__":
    main()
