#!/usr/bin/env python3
"""Generate src/variants/v3-icon-rich.html and src/variants/v4-real-logos.html
from the canonical src/profile.html via anchored string transforms."""
import re, sys

SRC = 'src/profile.html'
s = open(SRC).read()

def must(old, new, s, label):
    if old not in s:
        print(f"!! anchor not found: {label}", file=sys.stderr)
        sys.exit(1)
    return s.replace(old, new, 1)

LUC = lambda paths, extra='': f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" {extra}>{paths}</svg>'
ICONS = {
  'map-pin': LUC('<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>'),
  'medal': LUC('<circle cx="12" cy="15" r="6"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>'),
  'layers': LUC('<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>'),
  'sparkles': LUC('<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z"/>'),
  'building': LUC('<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>'),
  'compass': LUC('<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>'),
  'trending-up': LUC('<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>'),
  'terminal': LUC('<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>'),
  'briefcase': LUC('<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'),
  'users': LUC('<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
  'bot': LUC('<path d="M12 8V4H8"/><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>'),
  'wrench': LUC('<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'),
  'mail': LUC('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>'),
  'globe': LUC('<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>'),
  'linkedin': LUC('<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>'),
  'grad-cap': LUC('<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>'),
  'clock': LUC('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
  'star': LUC('<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'),
  'cpu': LUC('<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M9 2v2"/><path d="M9 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/>'),
}

# ---------------- v3 icon-rich ----------------
v3 = s

v3_css = '''
/* ---- v3 icon-rich additions ---- */
.sh-ico { width: 34px; height: 34px; color: var(--euc); align-self: center; opacity: 0.9; flex-shrink: 0; }
.sh-ico svg { width: 100%; height: 100%; }
.section-head { display: grid; grid-template-columns: auto 1fr; gap: 18px; align-items: center; }
.tile-ico { width: 26px; height: 26px; color: var(--euc); margin: 10px 0 2px; opacity: 0.95; }
.tile-ico svg { width: 100%; height: 100%; }
.spec-k { display: flex; align-items: center; gap: 6px; }
.spec-ico { width: 12px; height: 12px; color: var(--euc); flex-shrink: 0; }
.spec-ico svg { width: 100%; height: 100%; }
.engage li::before { content: none !important; }
.eng-ico { width: 20px; height: 20px; color: var(--euc); flex-shrink: 0; margin-right: 12px; transform: translateY(1px); }
.engage li { display: flex; align-items: flex-start; }
.engage li .eng-ico { margin-top: 2px; }
.c-ico { width: 13px; height: 13px; color: var(--euc); margin-right: 6px; transform: translateY(2px); display: inline-block; }
.edu-line { display: flex; align-items: flex-start; gap: 8px; }
.edu-ico { width: 15px; height: 15px; color: var(--cream-3); margin-top: 2px; flex-shrink: 0; }
.summary-ico { width: 13px; height: 13px; color: var(--euc); margin-right: 7px; transform: translateY(2px); display: inline-block; }
.hero .eyebrow .eb-ico { width: 12px; height: 12px; margin-left: 4px; transform: translateY(1.5px); display: inline-block; color: var(--euc); }
@media print {
  .sh-ico, .tile-ico, .spec-ico, .eng-ico, .c-ico, .edu-ico, .summary-ico, .eb-ico { display: none !important; }
  .section-head { gap: 8px; }
}
'''
v3 = must('</style>', v3_css + '\n</style>', v3, 'style close')

# Section-head icons
v3 = must('      <h2>Product, finance, architecture <span class="ital">&amp; operations.</span></h2>',
          '      <span class="sh-ico">'+ICONS['layers']+'</span>\n      <h2>Product, finance, architecture <span class="ital">&amp; operations.</span></h2>', v3, 'stack head')
v3 = must('      <h2>Executive competencies, <span class="ital">what I own at C-level.</span></h2>',
          '      <span class="sh-ico">'+ICONS['compass']+'</span>\n      <h2>Executive competencies, <span class="ital">what I own at C-level.</span></h2>', v3, 'skills head')
v3 = must('      <h2>Experience</h2>',
          '      <span class="sh-ico">'+ICONS['briefcase']+'</span>\n      <h2>Experience</h2>', v3, 'exp head')
v3 = must('      <h2>How I engage</h2>',
          '      <span class="sh-ico">'+ICONS['wrench']+'</span>\n      <h2>How I engage</h2>', v3, 'engage head')

# Tile icons (after each tag)
for num, ico in [('01</span>Product / CPO','compass'), ('02</span>Finance / CFO','trending-up'),
                 ('03</span>Operations / COO','layers'), ('04</span>Architecture / CTO','cpu')]:
    a = f'        <div class="tag"><span class="num">{num}</div>\n'
    v3 = must(a, a + f'        <div class="tile-ico">{ICONS[ico]}</div>\n', v3, 'tile '+num)

# Spec-cell icons
spec_map = [('Location','map-pin'), ('Founded','medal'), ('Stack','layers'), ('AI-native','sparkles'), ('Industries','building')]
for k, ico in spec_map:
    a = f'<div class="spec-k">{k}</div>'
    v3 = must(a, f'<div class="spec-k"><span class="spec-ico">{ICONS[ico]}</span>{k}</div>', v3, 'spec '+k)

# Engage icons
eng = [('<strong>Fractional &amp; interim CXO.</strong>','briefcase'),
       ('<strong>Transformation working groups, not lone turnarounds.</strong>','users'),
       ('<strong><em>AI-native</em> build-measure-learn.</strong>','bot')]
for strong, ico in eng:
    v3 = must(strong, f'<span class="eng-ico">{ICONS[ico]}</span>'+strong, v3, 'engage '+ico)

# Contact icons
v3 = must('<a href="mailto:marcus.callon@gmail.com">marcus.callon@gmail.com</a>',
          f'<a href="mailto:marcus.callon@gmail.com"><span class="c-ico">{ICONS["mail"]}</span>marcus.callon@gmail.com</a>', v3, 'c-mail')
v3 = must('<a href="https://notorious.kiwi">notorious.kiwi</a>',
          f'<a href="https://notorious.kiwi"><span class="c-ico">{ICONS["globe"]}</span>notorious.kiwi</a>', v3, 'c-web')
v3 = must('<a href="https://www.linkedin.com/in/marcuscallon">linkedin</a>',
          f'<a href="https://www.linkedin.com/in/marcuscallon"><span class="c-ico">{ICONS["linkedin"]}</span>linkedin</a>', v3, 'c-li')

# Summaries + edu icons
v3 = must('<summary>Clients &amp; employers (optional)</summary>',
          f'<summary><span class="summary-ico">{ICONS["users"]}</span>Clients &amp; employers (optional)</summary>', v3, 'clients summary')
v3 = must('<summary>Values &amp; signature (optional)</summary>',
          f'<summary><span class="summary-ico">{ICONS["star"]}</span>Values &amp; signature (optional)</summary>', v3, 'sig summary')
old_edu = '''    <div class="edu" data-reveal>
      <strong>Education</strong>
      <p>BCom — Accounting &amp; Finance, University of Otago</p>
      <p>BSc — Computer Science &amp; Information Science, University of Otago</p>'''
new_edu = '''    <div class="edu" data-reveal>
      <strong>Education</strong>
      <div class="edu-line"><span class="edu-ico">'''+ICONS['grad-cap']+'''</span><p>BCom — Accounting &amp; Finance, University of Otago</p></div>
      <div class="edu-line"><span class="edu-ico">'''+ICONS['grad-cap']+'''</span><p>BSc — Computer Science &amp; Information Science, University of Otago</p></div>'''
v3 = must(old_edu, new_edu, v3, 'edu icons')

# Title marker
v3 = v3.replace('<title>', '<title>[ICON-RICH] ').replace('data-theme', 'data-theme', 1)
open('src/variants/v3-icon-rich.html','w').write(v3)
print('v3-icon-rich.html written')

# ---------------- v4 real logos ----------------
v4 = s

v4_css = '''
/* ---- v4 real-logo additions ---- */
.rl { width: 42px; height: 42px; object-fit: contain; border-radius: 8px; display: block; }
.rl-fb { display: none; }
.role-logo .rl-fb { display: none; }
.rl.xpon { background: transparent; padding: 4px; }
.rl.wondaris { width: 15px; height: 15px; display: inline-block; vertical-align: -2px; margin: 0 1px; border-radius: 4px; }
.rl.holo-chip { width: 15px; height: 15px; display: inline-block; vertical-align: -2px; margin: 0 1px; border-radius: 4px; }
.rl.focal { height: 30px; width: auto; padding: 0; }
.rl.immersive { background: #fff; padding: 3px; }
.rl.qldt { width: 20px; height: 20px; display: inline-block; vertical-align: -4px; margin-right: 8px; }
.rl.otago { width: 120px; height: auto; display: block; margin-bottom: 10px; }
.cl-img { height: 24px; max-width: 96px; width: auto; object-fit: contain; display: block; border-radius: 4px; }
.cl-img.focal { height: 20px; }
.cl-img.immersive { background: #fff; padding: 2px; border-radius: 6px; }
@media print {
  .role-logo img.rl, .logo img.cl-img, .rl.wondaris, .rl.holo-chip, .rl.qldt, .rl.otago { display: none !important; }
  .rl-fb, .role-logo .rl-fb { display: block !important; }
}
'''
v4 = must('</style>', v4_css + '\n</style>', v4, 'style close')

# Role logos: wrap existing svg in rl-fb + add img before
role_logo_map = {
  'XPON': ('../assets/XPON_logomark_RGB-white@3x.png', 'xpon'),
  'Focal Labs': ('../assets/focal-labs-australia-logo.png', 'focal'),
  'Holoscribe': ('../assets/holoscribe-logo.png', ''),
  'Shorthand': ('../assets/shorthand-logo-black.svg?invert=1', ''),
  'Immersive': ('../assets/immersive_logo.jpeg', 'immersive'),
}

import html as _h
count = 0
def swap_role_logos(match_group, v):
    global count
    return v

# swap each role-logo div's svg with img + fallback svg
pattern = re.compile(r'(<div class="role-logo" title="([^"]+)">)(<svg[^>]*>.*?</svg>)(</div>)', re.S)
def repl(m):
    title = m.group(2)
    svg = m.group(3)
    key = None
    for k in role_logo_map:
        if k.lower() in title.lower():
            key = k; break
    if not key:
        return m.group(0)
    src, cls = role_logo_map[key]
    extra_style = ''
    img = f'<img class="rl {cls}" src="{src}" alt="{title}"{extra_style} loading="lazy">'
    # shorthand svg is dark on transparent: invert for dark bg on screen
    if key == 'Shorthand':
        img = f'<img class="rl" src="../assets/shorthand-logo-black.svg" alt="{title}" loading="lazy" style="filter:invert(0.88) brightness(1.06);">'
    return m.group(1) + img + f'<span class="rl-fb">{svg}</span>' + m.group(4)
v4, n_roles = pattern.subn(repl, v4)
print('role-logo swaps:', n_roles)

# Inline product chips in XPON bullets: Wondaris & Holoscribe
v4 = v4.replace('the Wondaris data platform',
                'the Wondaris <img class="rl wondaris" src="../assets/Wondaris_logomark_RGB-white_large.png" alt="Wondaris"> data platform', 1)
v4 = v4.replace('Holoscribe digital-publishing products.',
                'Holoscribe <img class="rl holo-chip" src="../assets/holoscribe-logo.png" alt="Holoscribe"> digital-publishing products.', 1)
v4 = v4.replace('the Wondaris customer-data platform and the Holoscribe digital-publishing platform',
                'the Wondaris <img class="rl wondaris" src="../assets/Wondaris_logomark_RGB-white_large.png" alt="Wondaris"> customer-data platform and the Holoscribe <img class="rl holo-chip" src="../assets/holoscribe-logo.png" alt="Holoscribe"> digital-publishing platform', 1)
v4 = v4.replace('from the ground up across Wondaris and Holoscribe.',
                'from the ground up across Wondaris <img class="rl wondaris" src="../assets/Wondaris_logomark_RGB-white_large.png" alt="Wondaris"> and Holoscribe <img class="rl holo-chip" src="../assets/holoscribe-logo.png" alt="Holoscribe">.', 1)

# Clients grid swap: XPON, Shorthand, Holoscribe, Immersive, Focal Labs
client_swaps = [
  ('<span class="logo" title="XPON Technologies (ASX:XPN)"><span class="wm sans-track">XPON</span></span>',
   '<span class="logo" title="XPON Technologies (ASX:XPN)"><img class="cl-img" src="../assets/XPON_logomark_RGB-white@3x.png" alt="XPON" loading="lazy"></span>'),
  ('<span class="logo feat" title="Shorthand"><span class="wm serif">Shorthand</span></span>',
   '<span class="logo feat" title="Shorthand"><img class="cl-img" src="../assets/shorthand-logo-black.svg" alt="Shorthand" loading="lazy" style="filter:invert(0.88) brightness(1.06);"></span>'),
  ('<span class="logo" title="Holoscribe"><span class="wm sans">Holoscribe</span></span>',
   '<span class="logo" title="Holoscribe"><img class="cl-img" src="../assets/holoscribe-logo.png" alt="Holoscribe" loading="lazy"></span>'),
  ('<span class="logo" title="Immersive"><span class="wm serif">Immersive</span></span>',
   '<span class="logo" title="Immersive"><img class="cl-img immersive" src="../assets/immersive_logo.jpeg" alt="Immersive" loading="lazy"></span>'),
  ('<span class="logo" title="Focal Labs"><span class="wm sans-track">FOCAL LABS</span></span>',
   '<span class="logo" title="Focal Labs"><img class="cl-img focal" src="../assets/focal-labs-australia-logo.png" alt="Focal Labs" loading="lazy"></span>'),
]
for old, new in client_swaps:
    v4 = must(old, new, v4, 'client '+old[:60])

# QLD Transport crest in the earlier row (web only)
v4 = must('<strong>Queensland Transport — Enterprise Solution Architect &amp; Lead Analyst/Developer.</strong>',
          '<img class="rl qldt" src="../assets/qld-transport.png" alt="Queensland Transport"><strong>Queensland Transport — Enterprise Solution Architect &amp; Lead Analyst/Developer.</strong>', v4, 'qldt crest')

# Otago crest above edu block
v4 = must('<strong>Education</strong>',
          '<img class="rl otago" src="../assets/university-of-otago.svg" alt="University of Otago" loading="lazy"><strong>Education</strong>', v4, 'otago crest')

v4 = v4.replace('<title>', '<title>[REAL-LOGOS] ')
open('src/variants/v4-real-logos.html','w').write(v4)
print('v4-real-logos.html written')
print('OK')
