# Tau Ceti progress board (demo)

**Live page:** https://roed-math.github.io/tauceti-progress-board/progress/

This is the Tau Ceti website's new **Progress** page exactly as the site would render it after
merging the `progress-page` branch
([compare](https://github.com/TauCetiProject/TauCeti/compare/main...roed-math:TauCeti-w2-fresh:progress-page)):
the HTML here was produced by the site's own Verso build from that branch, with the same
`static/style.css`, `static/progress.js` and generated `static/progress.json`. The Statistics page
is included too, since the branch adds a cross-link from it; Home and About link to the live site,
because those pages need the full library to build.

The generator, its tests, the topic map and the hand-read coverage file all live on the branch
(`scripts/roadmap_progress.py` and friends). Nothing here is maintained by hand any more.

`prototype.html` is the earlier standalone prototype this grew out of, kept for reference.
