# Scripts

## Obsidian SR Import

Use `import_obsidian_sr.py` to scan the Radiology Obsidian vault for spaced-repetition exchange-question notes and export compatible JSON into this project.

The importer treats the vault as read-only. It records hashes before and after the run and exits with an error if any source Markdown file changes.

```bash
python scripts/import_obsidian_sr.py --dry-run --report tmp/obsidian-sr-import-report.json
python scripts/import_obsidian_sr.py --merge-mode keep
```

Useful options:

- `--vault <path>`: Obsidian vault root. Defaults to the sibling `0筆記/Radiology` vault.
- `--target <path>`: `radiology-exam-review` root. Defaults to this project.
- `--dry-run`: parse and print/report counts without writing `data/{year}.json` or `data/index.json`.
- `--merge-mode keep|replace|update`: default `keep`; controls behavior when an imported deterministic id already exists.
- `--report <path>`: write a JSON report with scanned files, imported/skipped counts, skip reasons, fallback specialty decisions, and written files.

Question blocks are detected from SR structure: `#YYYY交換`, a `??` separator, and an `Ans:` line. Multiple year tags are exported as `years`; the canonical `year` is the earliest year. `#NR考` overrides YAML subspecialty, otherwise valid YAML `subspecialty` is used. Missing or broad YAML values are exported as `Unknown` with `subspecialty_confidence: "auto"` and are listed in the report.
