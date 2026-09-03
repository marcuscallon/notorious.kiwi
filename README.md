# Marcus Callon — Executive Profile

Dual-purpose executive profile: a dark, animated web page and a 2-page
print-ready PDF, both generated from the same source.

## Structure

```
content/            <-- EDIT THESE. Markdown + tiny frontmatter.
  meta.md               hero: name, thesis, stats, spec strip, contact
  stack.md              the 4 CXO pillar tiles
  competencies.md       the 4 executive-competency columns
  clients.md            grouped client/employer logo wall + print marquee;
                        `style: marks|words` toggles logomark tiles (hover
                        to reveal the org name) vs inline wordmarks
  roles/*.md            one file per experience role (frontmatter: start,
                        end, title, org, logo, tags; body: lede + bullets)
  earlier.md            the 2000-2013 history rows
  engage.md             how-I-engage bullets
  footer.md             education entries, pepeha lines + photo, footer contact

template.html       <-- the design shell (do not edit content here;
                        only structural/style work belongs here)
scripts/
  build.py            compiles content/*.md + template.html -> src/profile.html
  build-variants.py   writes src/variants/v3-icon-rich.html
src/profile.html    <-- GENERATED. Do not hand-edit.
src/variants/       <-- GENERATED comparisons (v3-icon-rich; v1/v2 are
                        older direction studies; v4-real-logos was promoted
                        into the canonical site in v12 and retired).
assets/             logos, headshot, pepeha photo, vendored flag icons
```

## Workflow

```bash
just site     # content -> website + variants
just pdf      # website + 2-page print-only PDF (needs node + the pdf skill's playwright)
```

The PDF is generated from a dedicated print-only stylesheet in
`scripts/print-layout.css`, which avoids mobile media-query leakage and gives
a clean, light A4 portrait output. The rendered file is
`Marcus-Callon-Executive-Profile.pdf`.

Directly (no just):

```bash
python3 scripts/build.py --variants
python3 scripts/build-print-direct.py
```

### Automatic PDF rebuild on commit

Install the local git hook once per clone. It will rebuild `just pdf`
automatically when you commit changes to `content/`, `template.html` or the
print build scripts, and stage the regenerated PDF for the same commit.

```bash
bash scripts/install-hooks.sh
```

## Rules of the road

- Edit only `content/*.md`. Run `just site`. Done.
- Comments: any line starting with `//` (indentation allowed) is ignored by
  the build - use it to disable entries or leave notes. Markdown has no
  native line comment; we use `//` instead of the noisy `<!-- -->`.
  Inline/trailing comments are not supported. Note `chip:` lines in
  stack.md are content, not comments.
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

## Deployment to notorious.kiwi

The generated site can be synced to the S3 bucket `notorious.kiwi`.

### One-time setup

1. Install [just](https://just.systems/) and the AWS CLI, then authenticate:
   ```bash
   brew install just awscli
   aws configure --profile notorious
   # or use SSO / environment variables
   ```
2. If the bucket is not already configured for static website hosting:
   ```bash
   AWS_PROFILE=notorious just deploy-setup
   ```

### Normal deploy

```bash
AWS_PROFILE=notorious just deploy
```

This:

- Runs `make site` to rebuild the site and variants.
- Syncs `src/` to `s3://notorious.kiwi/`.
- Copies `src/profile.html` to `s3://notorious.kiwi/index.html` so the root
  domain serves the profile.
- Invalidates the CloudFront distribution if you set
  `CLOUDFRONT_DISTRIBUTION_ID`.

Environment variables:

- `S3_BUCKET` (default: `notorious.kiwi`)
- `AWS_REGION` (default: `us-west-2`)
- `AWS_PROFILE` (optional)
- `CLOUDFRONT_DISTRIBUTION_ID` (optional)

Example with a CloudFront invalidation:

```bash
AWS_PROFILE=notorious \
  CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC \
  just deploy
```

## GitHub Actions (recommended)

A workflow at `.github/workflows/deploy.yml` deploys automatically on every push
to `main`.

### Setup

1. Create an IAM user for GitHub Actions and attach
   `scripts/aws-iam-policy.json`.
2. Generate an access key for that user.
3. In the GitHub repo, go to **Settings → Secrets and variables → Actions**
   and add:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

Pushes to `main` will then build the site and deploy it to S3 / CloudFront.

If you prefer OIDC later, swap the `Configure AWS credentials` step in the
workflow to use `role-to-assume` instead of access keys.
