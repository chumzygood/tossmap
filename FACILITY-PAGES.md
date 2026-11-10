# Facility pages and question evidence

Build and validate (from repository root):

```
python3 scripts/seed_data.py
python3 scripts/build.py
python3 scripts/test_facility_pages.py
```

`data/facility_details.json` is reviewed seed data, keyed by state, city and facility name. Each record pins the URL slug and keeps yes/no/unknown answers with the exact saved listing detail or official-source excerpt supporting them. Keep the existing slug when changing a facility name. `source_fields` contains explicit source-backed supplements to the older seed fields; `source_notice` surfaces operational warnings. Unknown is not a refusal. Conditional answers retain their conditions in the table and the matching visible FAQ schema. The source and original check date stay attached to each record.

`seed_data.py` merges these records into `facilities.json`. It invalidates answers and supplements if the original listing facts, source URL or check date change; re-review the details and update their fingerprint and source_checked value before restoring answers. New records get all unknown answers, rather than invented defaults. Operator unknowns are deliberately shown rather than inferred from a domain name or the publisher of a government page. Existing hours/fee text is preserved verbatim except where a reviewed supplement supplies a correction.

Facility URLs use `/<state>/<city>/<pinned-facility-slug>/`. The existing city-fragment Place @id is unchanged, while its `url` points to the facility page. City cards and material hubs link to the new pages. Material matching now uses affirmative explicit answers, not assumptions from omitted materials or broad automotive-fluid terminology.

All facility pages are in `sitemap.xml` and `/llms.txt`. `data/facility-indexing-queue.txt` is ordered for small manual daily indexing batches, not an automatic submission or a ranking guarantee. Its working copy is `/workspace/tossmap/indexing-queue.txt`; preserve progress outside the generated queue (or annotate a separate completion log) so rebuilding does not reset completed submissions. Do not submit all URLs at once. Original pending city/material requests (Louisville and /batteries/) remain separate daily tasks.

Nov 10 source review: 66 unique official URLs attempted, 57 returned HTTP 200 (Indianapolis was a JavaScript-only shell), 9 failed (403/500/SSL). Failed or content-empty fetches did not become new facts: their existing dated source-backed listing text was retained. Source snapshots and fetch outcomes are saved outside the repo at `/workspace/tossmap/source-review/`. New warnings/corrections include North Wake's fire-related closure with temporary Saturday collection and Wayne County's contractor appointment/fee requirements alongside its limited voucher program. No addresses were invented or expanded with guessed postal codes.

`data/facility-question-coverage.json` records the launch coverage. The test suite checks every facility's HTML and JSON-LD, visible FAQ parity, canonical/Place IDs, source and cross-links, material membership, unique queue/sitemap membership, and all internal HTML links. This is not a browser-based or independent multi-model UI approval.
