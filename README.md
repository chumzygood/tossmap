# Where to Toss It (dump directory)
Static site generated from `data/facilities.json` (official sources only, checked 2026-11-02).
- Edit data: `scripts/seed_data.py` → `python3 scripts/seed_data.py`
- Build: `python3 scripts/build.py` → `site/`
- Preview: `cd site && python3 -m http.server 8000`
- Before launch: set BASE in scripts/build.py, GoatCounter code, ad slots.
