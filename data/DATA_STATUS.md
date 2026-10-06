# Data status (civic-decoder)

**Nothing in `data/` has been independently verified.** Read this before using or citing any figure.

- These files were added in a single "initial release" commit on 2026-03-10 and never revised. No source URL, report page, or verification record exists in this repository: the `source` column names a publisher, not a document.
- At creation every row carried `verified = confirmed`, and a test required it. No evidence supports that. On 2026-10-05 every such flag was changed to `unverified`, and the test now requires that a row may claim `confirmed` only if `data/VERIFICATION_LOG.csv` records evidence for it (`file,row_key,evidence_url,verified_by,verified_on`). The log is empty.
- `cdf_seed.csv`: 12 of 14 constituencies carry the identical allocation and release (96.4 / 96.4), a placeholder-like pattern; real allocations vary.
- `cdf_seed.csv` and `mps_seed.csv` name office-holders that, as far as the reviewer knows from public record, did not hold the stated seat in FY2022/23 (for example a person listed as a constituency MP who became a governor or a Cabinet Secretary in 2022). Check each name against Parliament and IEBC records.
- `attendance_pct`, `bills_sponsored` and `questions_asked` describe named, real people. Do not publish or quote them without checking them against Hansard and the Parliament website.

To verify a row: open the cited report, check the figure, add a line to `VERIFICATION_LOG.csv` with the URL, your name and the date, then set the row's `verified` to `confirmed`.
