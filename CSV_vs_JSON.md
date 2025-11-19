# CSV vs JSON Data Format - Amara AI

## ✅ CSV Implementation (Current)

### Files Generated:
```
data/seed/
├── borrowers_seed.csv       (75 rows, ~50KB)
├── loans_seed.csv           (~150 rows, ~30KB)
├── repayments_seed.csv      (~3000 rows, ~200KB)
├── photos_seed.csv          (~200 rows, ~20KB)
└── field_notes_seed.csv     (~100 rows, ~80KB)
```

### Sample: borrowers_seed.csv
```csv
id,full_name,age,business_type,claimed_monthly_income,has_bank_account
1,Ibu Ratna Sari,38,Warung Gorengan (Fried Snacks Stall),2500000,false
2,Ibu Siti Nurhaliza,42,Jahit Pakaian (Tailoring),3200000,true
```

### Advantages ✅
- **Easy to inspect**: Open in Excel, Numbers, Google Sheets
- **Easy to edit**: Modify values directly in spreadsheet
- **Smaller file size**: ~380KB total vs ~450KB JSON
- **Standard format**: Universal compatibility
- **Version control friendly**: Git diffs show line changes clearly

### Disadvantages ⚠️
- **No nested data**: All data must be flat
- **Type information lost**: Everything is string (need conversion)
- **Special characters**: Commas in text need quotes
- **Multi-line text**: Field notes need careful escaping

---

## JSON Implementation (Alternative)

### Sample: borrowers_seed.json
```json
[
  {
    "id": 1,
    "full_name": "Ibu Ratna Sari",
    "age": 38,
    "business_type": "Warung Gorengan (Fried Snacks Stall)",
    "claimed_monthly_income": 2500000,
    "has_bank_account": false
  }
]
```

### Advantages ✅
- **Type preservation**: Numbers, booleans, null preserved
- **Nested structures**: Can have objects within objects
- **JSONB compatibility**: Direct insert to PostgreSQL JSONB fields
- **No escaping issues**: Handles quotes, commas naturally

### Disadvantages ⚠️
- **Harder to inspect**: Need JSON viewer or code editor
- **Not editable in Excel**: Requires specialized tools
- **Larger file size**: More verbose syntax
- **Git diffs**: Changes harder to see line-by-line

---

## Usage

### Generate CSV Data (Current Default)
```bash
python3 scripts/generate_dummy_data_csv.py
```

Output:
```
✅ Generated 75 borrowers
✅ Generated 150 loans
✅ Generated 3000 repayments
✅ Generated 200 photos
✅ Generated 100 field notes

Files saved in: data/seed/
  - borrowers_seed.csv
  - loans_seed.csv
  - repayments_seed.csv
  - photos_seed.csv
  - field_notes_seed.csv
```

### Seed Database (CSV)
```bash
python3 scripts/seed_database_csv.py
```

### Generate JSON Data (Alternative)
```bash
python3 scripts/generate_dummy_data.py
```

### Seed Database (JSON)
```bash
python3 scripts/seed_database.py
```

---

## Recommendation for Amara AI: CSV ✅

**Why CSV is better for this project:**

1. **Data Inspection**: You can open CSVs in Excel/Sheets to:
   - Verify borrower profiles look realistic
   - Check loan amounts are reasonable
   - Spot data quality issues quickly
   - Share with non-technical team members

2. **Manual Editing**: Easy to:
   - Add custom borrower scenarios
   - Fix typos in Indonesian text
   - Adjust income ranges
   - Create specific test cases

3. **Debugging**: When seeding fails:
   - See exactly which row has issues
   - Edit problematic data quickly
   - Re-run without regenerating everything

4. **Team Collaboration**:
   - Business team can review data
   - Field agents can validate narratives
   - Data analysts can do quick analysis

**CSV works well despite:**
- ⚠️ Indonesian text with commas → Python's csv module handles escaping automatically
- ⚠️ Multi-line field notes → Properly quoted in CSV
- ⚠️ Type conversion → Seeding script converts strings to correct types

---

## File Size Comparison

| Format | Total Size | Per Borrower |
|--------|-----------|--------------|
| CSV    | ~380 KB   | ~5 KB        |
| JSON   | ~450 KB   | ~6 KB        |

**Savings**: 70 KB (15% smaller) with CSV

---

## Both Scripts Available

You can use either format:

**CSV (Recommended)**:
- `scripts/generate_dummy_data_csv.py`
- `scripts/seed_database_csv.py`

**JSON (Alternative)**:
- `scripts/generate_dummy_data.py`
- `scripts/seed_database.py`

Both generate identical data, just different formats!
