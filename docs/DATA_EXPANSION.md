# Civic Decoder — Data Expansion Guide

## Current coverage (seed data)
| Resource | Seed | Full | Coverage |
|---|---|---|---|
| MPs (National Assembly) | 15 | 350 | 4.3% |
| Bills (13th Parliament) | 10 | ~200+ | ~5% |
| CDF constituencies | 14 | 290 | 4.8% |

---

## Path to full MP coverage

### Option A — Mzalendo (fastest, recommended)
Mzalendo maintains structured MP data for all 350 members.
Contact: **info@mzalendo.com** — request their parliamentary dataset for civic tech use.
They share it; cite them prominently in the app.

Minimum fields needed to expand `data/mps/mps_seed.csv`:
```
name, constituency, county, party, gender, elected_year,
attendance_pct, bills_sponsored, questions_asked
```
Attendance and bills data is in their annual Parliamentary Scorecards (PDF, published yearly).

### Option B — Parliament.go.ke scrape
parliament.go.ke/the-national-assembly/mps lists all members but requires JS rendering.
Use Playwright or Selenium to scrape:
```bash
pip install playwright
playwright install chromium
```
The page renders a table with: name, constituency, party, photo.
Attendance requires the Hansard records — considerably more work.

### Option C — IEBC open data
The IEBC publishes constituency boundary data and elected member lists
after each election. The 2022 results dataset includes all 290 elected MPs:
https://www.iebc.or.ke/results/

---

## Path to full CDF coverage

NG-CDF Annual Report 2023 covers all 290 constituencies.
The PDF is at: https://ngcdf.go.ke/annual-reports/
Fields: constituency, allocated (KSh M), utilised (KSh M), projects complete/total.

A one-time PDF extraction (pdfplumber) would yield all 290 rows.

---

## Schema for expanded mps_seed.csv

```csv
name,constituency,county,party,gender,elected_year,attendance_pct,
bills_sponsored,questions_asked,committees,source,verified
```

Fields with genuinely unknown values: use empty string, not 0.
Do not invent attendance figures — leave blank rather than estimate.

---

## Trust rules for any expansion
1. Every row must have a `source` and `verified` column.
2. Attendance figures must come from Hansard or Mzalendo scorecards — never estimated.
3. Bills sponsored must reference parliament.go.ke bill IDs.
4. CDF figures must reference the NG-CDF Annual Report year.
