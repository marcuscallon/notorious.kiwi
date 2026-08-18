# Marcus Callon — Executive Profile

Dual-purpose executive profile: a dark, animated web page and a 2-page
print-ready PDF, both generated from the same source.

## Structure

```
content/            <-- EDIT THESE. Markdown + tiny frontmatter.
  meta.md               hero: name, thesis, stats, spec strip, contact
  stack.md              the 4 CXO pillar tiles
  competencies.md       the 4 executive-competency columns
  clients.md            grouped client/employer logo wall + print marquee
  roles/*.md            one file per experience role (frontmatter: start,
                        end, title, org, logo, tags; body: lede + bullets)
  earlier.md            the 2000-2013 history rows
  engage.md             how-I-engage bullets
  signature.md          quote + VIA strengths (collapsed on the site)
  footer.md             education + footer contact

template.html       <-- the design shell (do not edit content here;
                        only structural/style work belongs here)
scripts/
  build.py            compiles content/*.md + template.html -> src/profile.html
  build-variants.py   writes src/variants/v3-icon-rich.html + v4-real-logos.html
src/profile.html    <-- GENERATED. Do not hand-edit.
src/variants/       <-- GENERATED comparisons (v3-icon-rich; v1/v2 are
                        older direction studies; v4-real-logos was promoted
                        into the canonical site in v12 and retired).
assets/             logos, headshot, pepeha photo, vendored flag icons
```

## Workflow

```bash
make site     # content -> website + variants
make pdf      # website + 2-page PDF (needs node + the pdf skill's playwright)
```

Or directly: `python3 scripts/build.py --variants --pdf`

## Rules of the road

- Edit only `content/*.md`. Run `make site`. Done.
- `src/profile.html` is regenerated on every build — hand edits are lost.
- Roles auto-sort by end date (`end: present` sorts first).
- Inline markdown: `**bold**`, `*italic*` (renders as the accent italic in
  headings/tiles, `<em>` in body text). `{mdash}` and `{travelflags}` are
  special tokens documented at the top of their sections.
- New role? Add `content/roles/NN-name.md` — logo key must be one of:
  xpon, 4impact, eqc, holoscribe, shorthand, immersive, focallabs
  (real logo files preferred; wordmark SVG fallbacks live in
  `scripts/build.py` ROLE_LOGOS along with per-logo dark-tile filters).
- After big content changes, check the PDF still fits 2 pages.
