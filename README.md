# Tau Ceti progress board (prototype)

A one-page overview of where every [Tau Ceti](https://github.com/TauCetiProject/TauCeti)
roadmap stands: one row per roadmap, one segment per layer, coloured by how much of that
layer the library has, beside the pull requests merged under the roadmap's label each week.

**Live page:** https://roed-math.github.io/tauceti-progress-board/

This is a demonstration for gathering feedback, not the real thing. The page itself explains
the design and what it would take to build it properly. The short version:

- The layer strips are read **by hand** from each roadmap's generated `STATUS.md` prose
  (`coverage.json`). The real build needs TauCetiProgress to emit a machine-readable per-layer
  verdict beside the prose (a `tauceti-coverage:v1` marker); that is the one upstream change the
  design asks for.
- Activity comes from the `roadmap/<Area>` labels on merged TauCeti pull requests, exactly as
  the site's Statistics page already uses them.
- Topics are a hand assignment (`topics.json`).
- The page belongs on the TauCeti site, regenerated every three hours by the Pages workflow
  that already clones TauCetiRoadmap and reads labels.

Deep links for demos: `?sort=topic`, `?sort=coverage`, `?sort=snapshot` (update due),
`?show=assessed`, `?show=completed`.

## Regenerating

```sh
python3 fetch_prs.py merged.json            # merged TauCeti PRs with labels, via gh (GraphQL)
gh pr list --repo TauCetiProject/TauCeti --state open --limit 1000 \
  --json number,title,labels,createdAt > open.json
(cd /path/to/TauCetiRoadmap && python3 /path/to/local_data.py /path/to/local.json)
python3 build_board.py                      # writes index.html
```

Then update `ROADMAP_HEAD`, `SNAPSHOT` and `TODAY` at the top of `build_board.py`, and add a
line to `coverage.json` for any roadmap that gained a `STATUS.md` (one character per layer:
`d`one, `p`artial, `u`ntouched, `?` unassessed, in README order).
