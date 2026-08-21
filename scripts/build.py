#!/usr/bin/env python3
"""Build src/profile.html from template.html + content/*.md.

Usage:
  python3 scripts/build.py           # build the site
  python3 scripts/build.py --variants   # site + regenerate v3/v4 variants
  python3 scripts/build.py --pdf        # site + PDF render (requires node)

Edit content/*.md, run this, refresh. Roles sort by end date (present first).
"""
import re, sys, html, glob, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---------------- tiny markdown/inline helpers ----------------

def esc(t):
    return html.escape(t, quote=False)

def inline(t, ital_class=None):
    """**bold** / *italic* inline. No HTML passthrough; raw chars escaped."""
    t = esc(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    def ital(m):
        body = m.group(1)
        return f'<span class="ital">{body}</span>' if ital_class else f'<em>{body}</em>'
    t = re.sub(r'\*(.+?)\*', ital, t)
    return t

def parse_keyvals(lines):
    out = {}
    cur_key = None
    for ln in lines:
        if ln.startswith('#') or not ln.strip():
            continue
        m = re.match(r'^([\w_]+):\s*(.*)$', ln)
        if m and not ln.startswith('- '):
            out[m.group(1)] = m.group(2).strip()
        elif ln.startswith('- '):
            out.setdefault(cur_key or 'items', [])
            if cur_key:
                out[cur_key] = out[cur_key] if isinstance(out[cur_key], list) else []
                out[cur_key].append(ln[2:].strip())
        else:
            pass
        if ln.startswith('- ') is False and re.match(r'^[\w_]+:', ln):
            cur_key = m.group(1)
    return out

def parse_sections(text):
    """Split a content file into '## ' blocks; returns (meta_lines, [(headline, body_lines)])."""
    text = text.replace('\r\n', '\n')
    parts = re.split(r'\n## ', '\n' + text.strip())
    meta_lines = parts[0].splitlines()
    blocks = []
    for part in parts[1:]:
        lines = part.splitlines()
        blocks.append(('## ' + lines[0], lines[1:]))
    return meta_lines, blocks

def section_heading(path, default=''):
    """Read the 'heading:' key from a markdown content file, inline-format it."""
    return heading_from_text(open(os.path.join(ROOT, path)).read(), default)

def heading_from_text(text, default=''):
    """Find first 'heading:' line and inline-format it."""
    for ln in text.splitlines():
        m = re.match(r'^heading:\s*(.*)$', ln)
        if m:
            return inline(m.group(1).strip(), ital_class=True)
    return inline(default, ital_class=True)

ICON_PATHS = {
  'compass': '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
  'trending-up': '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
  'layers': '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
  'terminal': '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>',
  'cpu': '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M9 2v2"/><path d="M9 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/>',
  'briefcase': '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
  'users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  'bot': '<path d="M12 8V4H8"/><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
  'sparkles': '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z"/>',
  'star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
  'building': '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
}
def icon(name, extra=''):
    p = ICON_PATHS.get(name, ICON_PATHS['compass'])
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}>{p}</svg>')

# ---------------- section generators ----------------

def gen_name(meta):
    def chars(line):
        out = []
        for ch in line:
            if ch == '.':
                out.append('<span class="period">.</span>')
            else:
                out.append(f'<span class="ch">{esc(ch)}</span>')
        return ''.join(out)
    l1 = meta.get('name_line1', 'Marcus')
    l2 = meta.get('name_line2', 'Callon.')
    return (f'    <h1 data-kinetic aria-label="{esc(l1 + " " + l2)}">\n'
            f'      <span class="ln" aria-hidden="true">{chars(l1)}</span>\n'
            f'      <span class="ln" aria-hidden="true">{chars(l2)}</span>\n'
            f'    </h1>')

def gen_thesis(meta):
    lines = meta.get('thesis', [])
    plain = ' '.join(re.sub(r'\*', '', l.replace('{mdash}', '-')) for l in lines)
    out = [f'    <p class="thesis" data-thesis aria-label="{esc(plain)}">']
    for ln in lines:
        ln = ln.replace('{mdash}', '§MDASH§')
        words = []
        for tok in ln.split(' '):
            if tok == '§MDASH§':
                words.append('<span class="period" style="color:var(--signal)">-</span>')
            elif tok.startswith('*') and tok.endswith('*'):
                words.append(f'<span class="wd"><em>{esc(tok.strip("*"))}</em></span>')
            else:
                words.append(f'<span class="wd">{esc(tok)}</span>')
        out.append(f'      <span class="ln" aria-hidden="true">{" ".join(words)}</span>')
    out.append('    </p>')
    return '\n'.join(out)

def gen_contact(meta):
    seps = '<span class="sep">·</span>'
    links = [f'<a href="{esc(h)}">{esc(lbl)}</a>' for lbl, h in
             (tuple(e.split(' = ', 1)) for e in meta.get('contact', []))]
    tail = esc(meta.get('contact_tail', ''))
    return '    <div class="contact" data-reveal>\n      ' + f'\n      {seps}\n      '.join(links) + \
           f'\n      {seps}\n      {tail}\n    </div>'

def gen_hero_facts(meta):
    stats = []
    for row in meta.get('stats', []):
        feat = ' feature' if row.endswith(':: feature') else ''
        row = row.replace(' :: feature', '')
        val, rest = row.split(' | ', 1)
        val_html = ''
        parts = val.split(' ', 1)
        if len(parts) == 2:
            val_html = f'{esc(parts[0])}<span class="u">{esc(parts[1])}</span>'
        else:
            val_html = esc(val)
        label = '<br>'.join(esc(x.strip()) for x in rest.split(';'))
        stats.append(f'''        <div class="stat{feat}">
          <div class="n">{val_html}</div>
          <div class="l">{label}</div>
        </div>''')
    # markets stat fixed chrome
    stats.append('''        <div class="stat markets-stat">
          <div class="n mkts"><span class="ac">AU</span> &middot; NZ &middot; UK</div>
          <div class="l">Markets served<br>Australia &middot; New Zealand &middot; United Kingdom</div>
        </div>''')
    cells = []
    for row in meta.get('spec', []):
        if ' = ' in row:
            k, v = row.split(' = ', 1)
            cells.append(f'      <div class="spec-cell"><div class="spec-k">{esc(k)}</div><div class="spec-v">{esc(v)}</div></div>')
        else:
            k, v = row.split(' | ', 1)
            items = []
            for it in v.split(';'):
                it = it.strip()
                m = re.fullmatch(r'\*(.+?)\*', it)
                items.append(f'<span><span class="ac">{esc(m.group(1))}</span></span>' if m else f'<span>{esc(it)}</span>')
            cells.append(f'      <div class="spec-cell"><div class="spec-k">{esc(k)}</div><div class="spec-v spec-list">{"".join(items)}</div></div>')
    return f'''    <div class="stats" data-reveal>
{os.linesep.join(stats)}
    </div>
    <div class="spec" data-reveal aria-label="Spec">
{os.linesep.join(cells)}
    </div>'''

def gen_stack(text):
    _, blocks = parse_sections(text)
    out = ['    <div class="stack">']
    for head, body in blocks:
        hm = re.match(r'## (\d+) :: (.+?) *(:: feature)?$', head.strip())
        num, tag, feat = hm.group(1), hm.group(2), bool(hm.group(3))
        feat_cls = ' tile-feature' if feat else ''
        title = None; paras = []; chip = None
        cur = None
        for ln in body:
            if ln.startswith('### '):
                title = ln[4:].strip()
            elif ln.startswith('chip:'):
                chip = ln[5:].strip()
            elif ln.strip():
                if cur is None: cur = []
                cur.append(ln.strip())
            else:
                if cur: paras.append(' '.join(cur)); cur = None
        if cur: paras.append(' '.join(cur))
        title_html = inline(title, ital_class=True)
        body_html = ''.join(f'\n        <p>{inline(p)}</p>' for p in paras)
        chip_html = f'\n        <span class="ai"><span class="d"></span>{esc(chip)}</span>' if chip else ''
        out.append(f'''      <div class="tile{feat_cls}" data-reveal>
        <div class="tag"><span class="num">{num}</span>{esc(tag)}</div>
        <h3>{title_html}</h3>{body_html}{chip_html}
      </div>''')
    out.append('    </div>')
    return '\n'.join(out)

def gen_competencies(text):
    _, blocks = parse_sections(text)
    out = ['    <div class="skills-grid" data-reveal>']
    for head, body in blocks:
        hm = re.match(r'## (\S+) :: (.+)$', head.strip())
        icon_name, title = hm.group(1), hm.group(2)
        title_html = inline(title, ital_class=True)
        lis = [ln[2:].strip() for ln in body if ln.startswith('- ')]
        lis_html = ''.join(f'\n          <li>{inline(li)}</li>' for li in lis)
        out.append(f'''      <div class="skill-col">
        <div class="skill-head">
          <span class="skill-icon" aria-hidden="true">{icon(icon_name)}</span>
          <div class="skill-k">{title_html}</div>
        </div>
        <ul class="skill-list">{lis_html}
        </ul>
      </div>''')
    out.append('    </div>')
    return '\n'.join(out)

def client_mark(name, style, feat, marks_mode=False):
    feat_cls = ' feat' if feat else ''
    t = esc(name)
    label = f'<span class="lg-name">{t}</span>' if marks_mode else ''
    if style == 'bbc':
        svg = ('<svg viewBox="0 0 90 30" aria-label="BBC"><g fill="currentColor">'
               '<rect x="0" y="0" width="26" height="30" rx="1"/><rect x="32" y="0" width="26" height="30" rx="1"/>'
               '<rect x="64" y="0" width="26" height="30" rx="1"/></g>'
               '<g fill="#15181C" font-family="Arial,sans-serif" font-weight="700" font-size="14" text-anchor="middle">'
               '<text x="13" y="21">B</text><text x="45" y="21">B</text><text x="77" y="21">C</text></g></svg>')
        inner = svg
    elif style == 'ft':
        inner = ('<svg viewBox="0 0 44 30" fill="none" aria-label="Financial Times">'
                 '<rect x="1" y="1" width="42" height="28" rx="2" stroke="currentColor" stroke-width="1.5"/>'
                 '<text x="22" y="21" text-anchor="middle" font-family="Georgia, serif" font-weight="700" font-size="15" '
                 'fill="currentColor">FT</text></svg>')
    elif style == 'mastercard':
        inner = ('<svg viewBox="0 0 48 30" aria-label="Mastercard">'
                 '<circle cx="18" cy="15" r="11" fill="currentColor" opacity="0.55"/>'
                 '<circle cx="30" cy="15" r="11" fill="currentColor" opacity="0.55" style="mix-blend-mode:screen"/></svg>')
    elif style == 'espn':
        return f'          <span class="logo espn{feat_cls}" title="{t}" tabindex="0"><span class="wm sans">{t}</span>{label}</span>'
    else:
        return f'          <span class="logo{feat_cls}" title="{t}" tabindex="0"><span class="wm {style}">{t}</span>{label}</span>'
    return f'          <span class="logo{feat_cls}" title="{t}" tabindex="0">{inner}{label}</span>'

def gen_clients(text):
    meta_lines, blocks = parse_sections(text)
    kv = parse_keyvals(meta_lines)
    mode = kv.get('style', 'words')  # 'words' (wordmark wall) or 'marks' (tile + hover name)
    marks_mode = (mode == 'marks')
    marquee_extra = kv.get('marquee_extra', '')
    names = []
    groups = []
    for head, body in blocks:
        gname = head[3:].strip()
        rows = []
        for ln in body:
            if ln.startswith('- '):
                ent = ln[2:].strip()
                feat = ent.endswith(' +')
                if feat: ent = ent[:-2].strip()
                nm, sty = ent.split(' = ', 1) if ' = ' in ent else (ent, 'sans')
                names.append(nm)
                rows.append(client_mark(nm.strip(), sty.strip(), feat, marks_mode))
        groups.append(f'''      <div class="logo-cat">
        <div class="cg-k">{esc(gname)}</div>
        <div class="logo-row">
{os.linesep.join(rows)}
        </div>
      </div>''')
    marquee = names[:]
    if marquee_extra: marquee.append(marquee_extra)
    marquee_html = ' &middot; '.join(esc(n) for n in marquee)
    mode_cls = ' mode-marks' if marks_mode else ''
    summary_title = heading_from_text(text, 'Clients & employers')
    return f'''  <details class="signature-group clients-group" id="clients" open>
    <summary>{summary_title}</summary>
    <div class="clients-print" aria-hidden="true">{marquee_html}</div>
    <div class="logo-grid{mode_cls}" data-reveal>
{os.linesep.join(groups)}
    </div>
  </details>'''

ROLE_LOGOS = {
  'xpon': ('XPON Technologies (ASX:XPN)', 'assets/XPON_logomark_RGB-white@3x.png', '',
           '<svg viewBox="0 0 60 30" fill="currentColor" aria-label="XPON"><text x="30" y="22" text-anchor="middle" font-family="Arial,sans-serif" font-weight="800" font-size="20" letter-spacing="-1">XPON</text></svg>'),
  '4impact': ('4impact', 'assets/4impact_logo.jpeg', 'filter: invert(1) grayscale(1);',
              '<svg viewBox="0 0 70 30" aria-label="4impact"><text x="35" y="23" text-anchor="middle" font-family="Arial,sans-serif" font-weight="800" font-size="22" fill="currentColor">4</text><text x="44" y="23" text-anchor="middle" font-family="Arial,sans-serif" font-weight="400" font-size="20" fill="currentColor">impact</text></svg>'),
  'eqc': ('EQC New Zealand', 'assets/naturalhazardscommission_logo.jpeg', 'filter: grayscale(1) brightness(1.15); mix-blend-mode: screen;',
          '<svg viewBox="0 0 50 30" aria-label="EQC"><rect x="2" y="4" width="46" height="22" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><text x="25" y="20" text-anchor="middle" font-family="Arial,sans-serif" font-weight="800" font-size="13" fill="currentColor">EQC</text></svg>'),
  'holoscribe': ('Holoscribe', 'assets/holoscribe-logo.png', '',
                 '<svg viewBox="0 0 70 24" aria-label="Holoscribe"><text x="35" y="18" text-anchor="middle" font-family="Georgia,serif" font-weight="700" font-style="italic" font-size="16" fill="currentColor">Holoscribe</text></svg>'),
  'shorthand': ('Shorthand', 'assets/shorthand-logo-black.svg', 'filter: invert(0.88) grayscale(1);',
                '<svg viewBox="0 0 70 24" aria-label="Shorthand"><text x="35" y="18" text-anchor="middle" font-family="Georgia,serif" font-weight="700" font-style="italic" font-size="17" fill="currentColor">Shorthand</text></svg>'),
  'immersive': ('Immersive', 'assets/immersive_logo.jpeg', 'filter: invert(1); border-radius: 3px;',
                '<svg viewBox="0 0 80 24" aria-label="Immersive"><text x="40" y="18" text-anchor="middle" font-family="Georgia,serif" font-weight="700" font-style="italic" font-size="18" fill="currentColor">Immersive</text></svg>'),
  'focallabs': ('Focal Labs', 'assets/focal-labs-australia-logo.png', 'mix-blend-mode: screen;',
                '<svg viewBox="0 0 80 24" aria-label="Focal Labs"><text x="40" y="18" text-anchor="middle" font-family="Arial,sans-serif" font-weight="800" font-size="13" letter-spacing="2" fill="currentColor">FOCAL LABS</text></svg>'),
}

def parse_role(path):
    s = open(path).read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', s, re.S)
    fm, body = m.group(1), m.group(2).strip()
    meta = {}
    for ln in fm.splitlines():
        k, v = ln.split(':', 1)
        meta[k.strip()] = v.strip()
    meta['tags_list'] = [t.strip() for t in meta.get('tags', '').split(',') if t.strip()]
    # body: paragraphs then bullets
    lede = None; bullets = []
    for blk in re.split(r'\n\s*\n', body):
        if blk.lstrip().startswith('- '):
            bullets += [ln[2:].strip() for ln in blk.splitlines() if ln.startswith('- ')]
        elif blk.strip():
            lede = blk.strip() if lede is None else lede + ' ' + blk.strip()
    meta['lede'], meta['bullets'] = lede, bullets
    return meta

def gen_roles():
    files = sorted(glob.glob('content/roles/*.md'))
    roles = [parse_role(f) for f in files]
    def end_key(r):
        e = r.get('end', '0')
        return (0, 9999) if e == 'present' else (1, -int(e))
    roles.sort(key=end_key)
    out = []
    for r in roles:
        start, end = r['start'], r['end']
        dur = '-present' if end == 'present' else (end if end == start else f'-{end}')
        logo_key = r.get('logo', '')
        title_attr, logo_file, logo_fx, logo_svg = ROLE_LOGOS[logo_key]
        if logo_file and os.path.exists(logo_file):
            inner = (f'<img class="rl" src="{logo_file}"' +
                     (f' style="{logo_fx}"' if logo_fx else '') +
                     f' alt="{title_attr}" loading="lazy"'
                     f' onerror="this.remove()">'
                     f'<span class="rl-fb" aria-label="{title_attr}">{logo_svg}</span>')
        else:
            inner = logo_svg
        lede_html = f'\n        <p class="lede">{inline(r["lede"])}</p>' if r['lede'] else ''
        bullets_html = ''
        if r['bullets']:
            lis = ''.join(f'\n          <li>{inline(b)}</li>' for b in r['bullets'])
            bullets_html = f'\n        <ul>{lis}\n        </ul>'
        tags = ''.join(f'<span>{esc(t)}</span>' for t in r['tags_list'])
        tags_html = f'\n        <div class="tags">{tags}</div>' if tags else ''
        out.append(f'''    <div class="role" data-reveal>
      <div class="role-yr">{esc(start)}<span class="dur">{esc(dur)}</span></div>
      <div class="role-logo" title="{title_attr}">{inner}</div>
      <div class="role-body">
        <h4>{inline(r["title"])} <span class="org"> - {inline(r["org"])}</span></h4>{lede_html}{bullets_html}{tags_html}
      </div>
    </div>''')
    return '\n\n'.join(out)

TRAVEL_FLAGS = ['sg','my','th','vn','hk','ie','gb','gr','tr','fr','nl','be','it','hr','hu','sk','pl','de','cz','at','li','ch','mc','es','pt','eg','us']

def gen_earlier(text):
    meta_lines, _ = parse_sections(text)
    kv_raw = {}
    rows = []
    cur_key = None
    for ln in meta_lines:
        if ln.startswith('#') or not ln.strip(): continue
        if ln.startswith('- '):
            rows.append(ln[2:].strip())
        else:
            m = re.match(r'^(\w+):\s*(.*)$', ln)
            if m:
                kv_raw[m.group(1)] = m.group(2)
    heading = kv_raw.get('heading', 'Earlier')
    out = [f'''    <details class="earlier" data-reveal>
      <summary class="cg-k">{esc(heading)}</summary>
''']
    for row in rows:
        yrs, desc = row.split(' | ', 1)
        desc = inline(desc)
        if '{travelflags}' in desc:
            flags = ''.join(f'<img src="assets/flags/{c}.svg" alt="" loading="lazy">' for c in TRAVEL_FLAGS)
            desc = desc.replace('{travelflags}', f'<div class="travel-flags" aria-hidden="true">{flags}</div>')
        out.append(f'      <div class="earlier-row"><div class="yr">{esc(yrs)}</div><div class="desc">{desc}</div></div>')
    out.append('    </details>')
    return '\n'.join(out)

def gen_engage(text):
    meta_lines, _ = parse_sections(text)
    items = []
    for ln in meta_lines:
        if ln.startswith('- '):
            items.append(ln[2:].strip())
    lis = []
    for it in items:
        m = re.match(r'^\*\*(.+?)\*\*\s*(.*)$', esc(it))
        if not m:
            lis.append(f'      <li data-reveal>{inline(it)}</li>')
            continue
        head, rest = m.group(1), m.group(2)
        head = re.sub(r'\*(.+?)\*', r'<em>\1</em>', head)
        rest_html = f' <span class="engage-desc">{rest}</span>' if rest else ''
        lis.append(f'      <li data-reveal><strong>{head}</strong>{rest_html}</li>')
    return '    <ul>\n' + '\n'.join(lis) + '\n    </ul>'

def gen_signature(text):
    kv = {}
    strengths = []
    cur = None
    for ln in text.splitlines():
        if ln.startswith('#') or not ln.strip(): continue
        if ln.startswith('- '):
            strengths.append(ln[2:].strip())
        else:
            m = re.match(r'^(\w+):\s*(.*)$', ln)
            if m: kv[m.group(1)] = m.group(2)
    s_lis = '\n'.join(f'          <li>{esc(x)}</li>' for x in strengths)
    return f'''  <details class="signature-group">
    <summary>Values &amp; signature</summary>
    <section class="signature">
      <blockquote class="sig-quote">
        &#8220;{esc(kv.get('quote',''))}&#8221;
        <cite>{esc(kv.get('cite',''))}</cite>
      </blockquote>
      <div class="strengths">
        <strong>VIA Character Strengths</strong>
        <ul class="strengths-list">
{s_lis}
        </ul>
      </div>
    </section>
  </details>'''

def gen_footer(text):
    kv = {}
    lists = {}
    cur_key = None
    for ln in text.splitlines():
        if ln.startswith('#') or not ln.strip(): continue
        if ln.startswith('- '):
            lists.setdefault(cur_key, []).append(ln[2:].strip())
        else:
            m = re.match(r'^(\w+):\s*(.*)$', ln)
            if m:
                kv[m.group(1)] = m.group(2); cur_key = m.group(1)
    edu_html = '\n'.join(f'          <p>{esc(e)}</p>' for e in lists.get('edu', []))
    edu_sec = f'''<section class="edu-sec" data-reveal>
    <div class="cg-k">Education</div>
    <div class="edu-row">
      <img class="edu-logo" src="assets/university-of-otago.svg" alt="University of Otago">
      <div class="edu-lines">
{edu_html}
      </div>
    </div>
  </section>
'''
    pepeha = lists.get('pepeha', [])
    pp_html = ''
    if pepeha:
        pp_lines = '\n'.join(f'          <span>{esc(l)}</span>' for l in pepeha)
        img, alt = kv.get('pepeha_img', ''), kv.get('pepeha_img_alt', '')
        img_html = (f'<div class="pp-imgwrap" aria-hidden="true">'
                    f'<img src="{esc(img)}" alt="{esc(alt)}"></div>') if img else ''
        what = kv.get('pepeha_what', '')
        what_html = f'<span class="pp-what" aria-hidden="true">{esc(what)}</span>' if what else ''
        pp_html = f'''<details class="pepeha">
    <summary>Pepeha{what_html}</summary>
    <div class="pp-body">
      <div class="pp-lines" tabindex="0">
{pp_lines}
      </div>
      {img_html}
    </div>
  </details>
'''
    return edu_sec + pp_html + f'''  <footer class="foot">
    <div class="meta" style="grid-column: 1 / -1; text-align: center; justify-self: center;">
      {esc(kv.get('meta_name',''))} &middot;
      <a href="{esc(kv.get('meta_link_href',''))}">{esc(kv.get('meta_link_label',''))}</a>
    </div>
  </footer>'''

def gen_cta(text):
    kv = {}
    for ln in text.splitlines():
        if ln.startswith('#') or not ln.strip():
            continue
        m = re.match(r'^(cta_\w+):\s*(.*)$', ln)
        if m:
            kv[m.group(1)] = m.group(2).strip()
    heading = inline(kv.get('cta_heading', 'Start a conversation.'), ital_class=True)
    body = inline(kv.get('cta_body', ''), ital_class=True)
    btn = esc(kv.get('cta_button', 'Email'))
    href = esc(kv.get('cta_href', 'mailto:marcus.callon@gmail.com'))
    return {
        'heading': heading,
        'body': body,
        'button': btn,
        'href': href,
    }



tpl = open('template.html').read()
meta_txt = open('content/meta.md').read()
mlines = meta_txt.splitlines()
meta_kv = {}
cur_key = None
for ln in mlines:
    if ln.startswith('#') or not ln.strip(): continue
    if ln.startswith('- '):
        v = meta_kv.get(cur_key, [])
        if not isinstance(v, list):
            v = [] if not v else [v]
        v.append(ln[2:].strip())
        meta_kv[cur_key] = v
    else:
        m = re.match(r'^(\w+):\s*(.*)$', ln)
        if m:
            meta_kv[m.group(1)] = m.group(2); cur_key = m.group(1)
# theses/stats/spec/contact were collected as list items under their keys

out = tpl
out = out.replace('<title>Marcus Callon — Executive Profile</title>', f'<title>{esc(meta_kv.get("title", "Marcus Callon"))}</title>')
out = out.replace('{{NAME}}', gen_name(meta_kv))
out = out.replace('{{THESIS}}', gen_thesis(meta_kv))
out = out.replace('{{CONTACT}}', gen_contact(meta_kv))
out = out.replace('{{HERO_FACTS}}', gen_hero_facts(meta_kv))
out = out.replace('{{STACK_TITLE}}', section_heading('content/stack.md', 'Product, finance, architecture *& operations.*'))
out = out.replace('{{STACK}}', gen_stack(open('content/stack.md').read()))
out = out.replace('{{COMPETENCIES_TITLE}}', section_heading('content/competencies.md', 'Executive competencies, *what I own at C-level.*'))
out = out.replace('{{COMPETENCIES}}', gen_competencies(open('content/competencies.md').read()))
out = out.replace('{{CLIENTS}}', gen_clients(open('content/clients.md').read()))
out = out.replace('{{EXPERIENCE_TITLE}}', section_heading('content/experience.md', 'Experience'))
out = out.replace('{{ROLES}}', gen_roles())
out = out.replace('{{EARLIER_ROWS}}', gen_earlier(open('content/earlier.md').read()))
out = out.replace('{{ENGAGE_TITLE}}', section_heading('content/engage.md', 'How I engage'))
out = out.replace('{{ENGAGE_UL}}', gen_engage(open('content/engage.md').read()))
# signature section removed in v13.
cta = gen_cta(open('content/cta.md').read())
out = out.replace('{{CTA_HEADING}}', cta['heading'])
out = out.replace('{{CTA_BODY}}', cta['body'])
out = out.replace('{{CTA_BUTTON}}', cta['button'])
out = out.replace('{{CTA_HREF}}', cta['href'])
out = out.replace('{{FOOTER}}', gen_footer(open('content/footer.md').read()))

def inject_print_css(html):
    """Replace the template's @media print block with the latest print-layout.css."""
    css_path = os.path.join(ROOT, 'scripts', 'print-layout.css')
    try:
        css = open(css_path).read()
    except FileNotFoundError:
        return html
    # Remove the leading @page rule from print-layout.css because we will
    # place it outside the @media print wrapper (nested @page is invalid).
    lines = css.splitlines()
    if lines and lines[0].strip().startswith('@page'):
        css = '\n'.join(lines[1:]).lstrip('\n')
    marker = '/* ============================================\n   PRINT / PDF - auto-injected from scripts/print-layout.css\n   ============================================ */'
    idx = html.find(marker)
    if idx == -1:
        return html
    end = html.find('</style>', idx)
    if end == -1:
        return html
    injected = (
        marker + '\n'
        '@page { size: A4 portrait; margin: 7mm 10mm 5mm; }\n'
        '@media print {\n' + css + '\n}\n'
        '</style>'
    )
    return html[:idx] + injected + html[end + len('</style>'):]


def externalize_links(html):
    """Add target=_blank rel=noopener to external http(s) links only."""
    def patch(m):
        tag = m.group(0)
        hm = re.search(r'href=["\']([^"\']+)["\']', tag, re.I)
        if not hm:
            return tag
        href = hm.group(1)
        if not re.match(r'^(https?:)?//', href, re.I):
            return tag
        # avoid duplicate attributes
        tag = re.sub(r'\s+target=["\'][^"\']*["\']', '', tag, flags=re.I)
        tag = re.sub(r'\s+rel=["\'][^"\']*["\']', '', tag, flags=re.I)
        return tag.rstrip('>') + ' target="_blank" rel="noopener">'
    return re.sub(r'<a\b[^>]*>', patch, html, flags=re.I)

leftover = re.findall(r'\{\{[A-Z_]+\}\}', out)
if leftover:
    print('!! leftover slots:', leftover, file=sys.stderr); sys.exit(1)

out = inject_print_css(out)
out = externalize_links(out)

open('src/profile.html', 'w').write(out)
print('built src/profile.html (%d bytes)' % len(out))

if '--variants' in sys.argv:
    subprocess.run([sys.executable, 'scripts/build-variants.py'], check=True)

if '--pdf' in sys.argv:
    subprocess.run(['node', os.path.expanduser(
        '~/.pi/agent/skills/pdf/scripts/html-to-pdf.mjs'),
        '--file', 'src/profile.html', '-o', 'Marcus-Callon-Executive-Profile.pdf',
        '--no-footer'], check=True)
    print('rendered Marcus-Callon-Executive-Profile.pdf')
