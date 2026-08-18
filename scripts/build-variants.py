#!/usr/bin/env python3
"""Generate variants from canonical src/profile.html.
v3-icon-rich: tile + engage + summary + edu icons ONLY (review verdict:
  section-head/spec/contact icons broke the left edge / were fussy).
v4-real-logos: real logo images ONLY in role headers on uniform grayscale
  cards with print fallbacks to the built wordmarks (review verdict: inline
  chips / colored marks break the two-accent discipline)."""
import re, sys

SRC = 'src/profile.html'
s = open(SRC).read()

def must(old, new, s, label):
    if old not in s:
        print(f"!! anchor not found: {label}", file=sys.stderr); sys.exit(1)
    return s.replace(old, new, 1)

LUC = lambda paths: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'
ICONS = {
  'compass': LUC('<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>'),
  'trending-up': LUC('<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>'),
  'terminal': LUC('<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>'),
  'briefcase': LUC('<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'),
  'users': LUC('<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
  'bot': LUC('<path d="M12 8V4H8"/><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>'),
  'layers': LUC('<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>'),
  'star': LUC('<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'),
  'grad-cap': LUC('<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>'),
  'cpu': LUC('<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M9 2v2"/><path d="M9 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/>'),
}

# ---------------- v3 icon-rich (culled per review) ----------------
v3 = s
v3_css = '''
/* ---- v3 icon-rich additions (review-culled set) ---- */
.tile-ico { width: 24px; height: 24px; color: var(--euc); margin: 12px 0 2px; opacity: 0.95; }
.tile-ico svg { width: 100%; height: 100%; }
.engage li::before { content: none !important; }
.engage li { display: flex; align-items: flex-start; }
.eng-ico { width: 20px; height: 20px; color: var(--euc); flex-shrink: 0; margin: 2px 12px 0 0; }
.summary-ico { width: 13px; height: 13px; color: var(--euc); margin-right: 7px; transform: translateY(2px); display: inline-block; }
.edu-line { display: flex; align-items: flex-start; gap: 8px; }
.edu-ico { width: 15px; height: 15px; color: var(--cream-3); margin-top: 2px; flex-shrink: 0; }
@media print {
  .tile-ico, .eng-ico, .summary-ico, .edu-ico { display: none !important; }
}
'''
v3 = must('</style>', v3_css + '\n</style>', v3, 'style close')
for num, ico in [('01</span>Product / CPO','compass'), ('02</span>Finance / CFO','trending-up'),
                 ('03</span>Operations / COO','layers'), ('04</span>Architecture / CTO','cpu')]:
    a = f'        <div class="tag"><span class="num">{num}</div>\n'
    v3 = must(a, a + f'        <div class="tile-ico">{ICONS[ico]}</div>\n', v3, 'tile '+num)
eng = [('<strong>Fractional &amp; interim CXO.</strong>','briefcase'),
       ('<strong>Transformation working groups, not lone turnarounds.</strong>','users'),
       ('<strong><em>AI-native</em> build-measure-learn.</strong>','bot')]
for strong, ico in eng:
    v3 = must(strong, f'<span class="eng-ico">{ICONS[ico]}</span>'+strong, v3, 'engage '+ico)
v3 = must('<summary>Clients &amp; employers</summary>',
          f'<summary><span class="summary-ico">{ICONS["users"]}</span>Clients &amp; employers</summary>', v3, 'clients summary')
v3 = must('<summary>Values &amp; signature</summary>',
          f'<summary><span class="summary-ico">{ICONS["star"]}</span>Values &amp; signature</summary>', v3, 'sig summary')
old_edu = '''    <div class="edu" data-reveal>
      <strong>Education</strong>
      <p>BCom — Accounting &amp; Finance, University of Otago</p>
      <p>BSc — Computer Science &amp; Information Science, University of Otago</p>'''
new_edu = '''    <div class="edu" data-reveal>
      <strong>Education</strong>
      <div class="edu-line"><span class="edu-ico">'''+ICONS['grad-cap']+'''</span><p>BCom — Accounting &amp; Finance, University of Otago</p></div>
      <div class="edu-line"><span class="edu-ico">'''+ICONS['grad-cap']+'''</span><p>BSc — Computer Science &amp; Information Science, University of Otago</p></div>'''
v3 = must(old_edu, new_edu, v3, 'edu icons')
v3 = v3.replace('<title>', '<title>[ICON-RICH] ')
open('src/variants/v3-icon-rich.html','w').write(v3)
print('v3-icon-rich.html written')

# ---------------- v4 real logos (role headers only, grayscale-unified) ----------------
v4 = s
v4_css = '''
/* ---- v4 real-logo additions: role headers only, unified monochrome ---- */
.role-logo img.rl { width: 40px; height: 40px; object-fit: contain; display: block;
                    filter: grayscale(1) contrast(1.02) opacity(0.92); }
.role-logo img.rl.focal { width: 64px; height: auto; }
.role-logo img.rl.shorthand { filter: grayscale(1) invert(0.88) brightness(1.06) opacity(0.92); }
.rl-fb { display: none !important; }
.rl.qldt { width: 22px; height: 22px; display: inline-block; vertical-align: -4px; margin-right: 8px;
           filter: grayscale(1) invert(0.88) brightness(1.05) opacity(0.85); border-radius: 50%; }
@media print {
  .role-logo img.rl, .rl.qldt { display: none !important; }
  .rl-fb { display: block !important; }
}
'''
v4 = must('</style>', v4_css + '\n</style>', v4, 'style close')

role_files = {
  'XPON Technologies': '../assets/XPON_logomark_RGB-white@3x.png',
  'Focal Labs': '../assets/focal-labs-australia-logo.png',
  'Holoscribe': '../assets/holoscribe-logo.png',
  'Shorthand': '../assets/shorthand-logo-black.svg',
  'Immersive': '../assets/immersive_logo.jpeg',
}
def extra_cls(t):
    if 'Shorthand' in t: return 'shorthand'
    if 'Focal' in t: return 'focal'
    return ''
pattern = re.compile(r'(<div class="role-logo" title="([^"]+)">)(<svg[^>]*>.*?</svg>)(</div>)', re.S)
def repl(m):
    title, svg = m.group(2), m.group(3)
    key = next((k for k in role_files if k.lower() in title.lower()), None)
    if not key: return m.group(0)
    img = f'<img class="rl {extra_cls(title)}" src="{role_files[key]}" alt="{title}" loading="lazy">'
    return m.group(1) + img + f'<span class="rl-fb">{svg}</span>' + m.group(4)
v4, n = pattern.subn(repl, v4)
print('role-logo swaps:', n)

v4 = must('<strong>Queensland Transport — Enterprise Solution Architect &amp; Lead Analyst/Developer.</strong>',
          '<img class="rl qldt" src="../assets/qld-transport.png" alt=""><strong>Queensland Transport — Enterprise Solution Architect &amp; Lead Analyst/Developer.</strong>', v4, 'qldt crest')
v4 = v4.replace('<title>', '<title>[REAL-LOGOS] ')
open('src/variants/v4-real-logos.html','w').write(v4)
print('v4-real-logos.html written')
print('OK')
