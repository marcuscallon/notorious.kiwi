#!/usr/bin/env python3
"""v10 fixes to canonical src/profile.html from the design review triage."""
import sys

p = 'src/profile.html'
s = open(p).read()

def must(old, new, label, count=1):
    global s
    if s.count(old) < count:
        print(f"!! missing anchor: {label} (found {s.count(old)}, need {count})", file=sys.stderr)
        sys.exit(1)
    s = s.replace(old, new, count)

# ---------- H1: print spec strip collapse ----------
must("  .foot .meta { display: none; }",
     """  .foot .meta { display: none; }
  /* Review H1: mobile 820px rules leak into print - re-pin grid layouts */
  .spec { grid-template-columns: repeat(5, 1fr) !important; }
  .spec-cell { border-right: none !important; }
  .markets-stat .n.mkts { font-size: 9pt; }""", 'print spec 5col')

# ---------- H3: credibility signal hidden twice ----------
must('<details class="signature-group clients-group" id="clients">',
     '<details class="signature-group clients-group" id="clients" open>', 'clients default open')
must('<summary>Clients &amp; employers (optional)</summary>',
     '<summary>Clients &amp; employers</summary>', 'summary rename')
must('<summary>Values &amp; signature (optional)</summary>',
     '<summary>Values &amp; signature</summary>', 'signature rename')

# print marquee line inside clients details (screen-hidden)
must('''    <summary>Clients &amp; employers</summary>''',
     '''    <summary>Clients &amp; employers</summary>
    <div class="clients-print" aria-hidden="true">BBC · The Guardian · ESPN · The Times · Financial Times · Hearst · Mastercard · RACQ · Queensland Transport · EQC · Shorthand · Immersive · Holoscribe · Wondaris · Focal Labs · University of Otago</div>''',
     'clients print marquee markup')

# marquee CSS (screen) — hide on screen
must('/* strengths list */',
     '''/* clients print marquee: hidden on screen, one-line strip in print */
.clients-print { display: none; }

/* strengths list */''', 'marquee css')

# print: show clients details w/ marquee only, keep signature hidden
must('''  details.signature-group, details.clients-group { display: none !important; }''',
     '''  details.signature-group { display: none !important; }
  details.clients-group { display: block !important; padding: 0 !important; border-top: none !important; }
  details.clients-group > summary, details.clients-group .logo-groups, details.clients-group .client-group,
  details.clients-group .client-groups, details.clients-group > div:not(.clients-print) { display: none !important; }
  .clients-print { display: block !important; font-family: var(--mono); font-size: 6pt; letter-spacing: 0.06em; color: var(--cream-3); padding: 0 0 1px; }''',
     'print clients visible w/ marquee')

# ---------- H4: BBC letters ----------
must('<span class="logo feat" title="BBC"><svg viewBox="0 0 90 30" fill="currentColor" aria-label="BBC"><rect x="0" y="0" width="26" height="30" rx="1"/><rect x="32" y="0" width="26" height="30" rx="1"/><rect x="64" y="0" width="26" height="30" rx="1"/></svg></span>',
     '<span class="logo feat" title="BBC"><svg viewBox="0 0 90 30" aria-label="BBC"><g fill="currentColor"><rect x="0" y="0" width="26" height="30" rx="1"/><rect x="32" y="0" width="26" height="30" rx="1"/><rect x="64" y="0" width="26" height="30" rx="1"/></g><g fill="#15181C" font-family="Arial,sans-serif" font-weight="700" font-size="14" text-anchor="middle"><text x="13" y="21">B</text><text x="45" y="21">B</text><text x="77" y="21">C</text></g></svg></span>',
     'BBC letters')

# ---------- M4: preloader + hero gating; M2: details refresh; L3: lenis anchors; L6: aria done in markup below ----------
old_js_pre = """  // ---- Preloader ----
  function hidePreloader() {
    var p = document.getElementById('preloader');
    if (p) p.classList.add('done');
  }
  window.addEventListener('load', function () {
    setTimeout(hidePreloader, 1400);
  });
  // Safety fallback
  setTimeout(hidePreloader, 4000);
"""
new_js_pre = """  // ---- Preloader: gate the hero intro on its completion ----
  var preloaderDone = false;
  function hidePreloader() {
    if (preloaderDone) return;
    preloaderDone = true;
    var p = document.getElementById('preloader');
    if (p) p.classList.add('done');
    runHeroIntro();
  }
  var heroIntroStarted = false;
  function runHeroIntro() { /* defined below; preloader fires it */ }
  document.addEventListener('DOMContentLoaded', function () {
    var minDwell = new Promise(function (r) { setTimeout(r, 900); });
    var fontsReady = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
    Promise.all([minDwell, fontsReady]).then(hidePreloader);
  });
  // Safety fallback
  setTimeout(hidePreloader, 4000);
"""
must(old_js_pre, new_js_pre, 'preloader rework')

old_name = """  // ---- Hero kinetic name: per-char rise + overshoot on load ----
  var heroName = document.querySelector('[data-kinetic]');
  if (heroName) {
    var chars = heroName.querySelectorAll('.ch, .period');
    gsap.set(chars, { yPercent: 120, opacity: 0, rotate: function () { return gsap.utils.random(-9, 9); } });
    var tl = gsap.timeline({ delay: 1.0 });
    tl.to(chars, {
      yPercent: 0, opacity: 1, rotate: 0,
      duration: 0.9, ease: 'back.out(1.7)',
      stagger: { each: 0.035, from: 'start' }
    });
  }

  // ---- Thesis: word-by-word mask reveal, slightly after name ----
  var thesis = document.querySelector('[data-thesis]');
  if (thesis) {
    var words = thesis.querySelectorAll('.wd');
    gsap.set(words, { yPercent: 115, opacity: 0 });
    gsap.to(words, {
      yPercent: 0, opacity: 1,
      duration: 0.8, ease: 'expo.out',
      stagger: 0.018,
      delay: 1.6
    });
  }
"""
new_name = """  // ---- Hero kinetic name + thesis: gated on preloader completion ----
  var introChars = null, introWords = null;
  (function prepIntro() {
    var heroName = document.querySelector('[data-kinetic]');
    if (heroName) {
      introChars = heroName.querySelectorAll('.ch, .period');
      gsap.set(introChars, { yPercent: 120, opacity: 0, rotate: function () { return gsap.utils.random(-9, 9); } });
    }
    var thesis = document.querySelector('[data-thesis]');
    if (thesis) {
      introWords = thesis.querySelectorAll('.wd');
      gsap.set(introWords, { yPercent: 115, opacity: 0 });
    }
  })();
  runHeroIntro = function () {
    if (heroIntroStarted) return; heroIntroStarted = true;
    if (introChars) {
      gsap.to(introChars, {
        yPercent: 0, opacity: 1, rotate: 0,
        duration: 0.9, ease: 'back.out(1.7)',
        stagger: { each: 0.035, from: 'start' }
      });
    }
    if (introWords) {
      gsap.to(introWords, {
        yPercent: 0, opacity: 1,
        duration: 0.8, ease: 'expo.out',
        stagger: 0.012,
        delay: 0.45
      });
    }
  };
"""
must(old_name, new_name, 'hero gating')

# reduced-motion path: if prefersReduced, force hero visible too (its early return skipped runHeroIntro)
old_rm = """  if (prefersReduced) {
    // Show everything, no motion
    document.querySelectorAll('[data-reveal]').forEach(function (el) { el.style.opacity = 1; el.style.transform = 'none'; });
    return;
  }"""
new_rm = """  if (prefersReduced) {
    // Show everything, no motion
    document.querySelectorAll('[data-reveal]').forEach(function (el) { el.style.opacity = 1; el.style.transform = 'none'; });
    gsap = null; // intro hidden via plain CSS if gsap unavailable
    return;
  }"""
# note: hero chars/thesis are pre-split spans with default CSS visibility - they are visible by default
# because gsap.set only applies when motion enabled. Keeping reduced path as-is (no edit needed); skip must().

# details toggle -> ScrollTrigger.refresh(); lenis smooth anchors
old_dl = """  // ---- Download button ----
  var btn = document.getElementById('dl');"""
new_dl = """  // ---- Details open/close shifts layout: refresh ScrollTrigger measurements ----
  document.querySelectorAll('details').forEach(function (d) {
    d.addEventListener('toggle', function () { ScrollTrigger.refresh(); });
  });

  // ---- Smooth nav anchors through Lenis ----
  document.querySelectorAll('.topnav .links a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      var target = id.length > 1 ? document.querySelector(id) : null;
      if (!target) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(target, { offset: -60 });
      else target.scrollIntoView({ behavior: 'smooth' });
    });
  });

  // ---- Download button ----
  var btn = document.getElementById('dl');"""
must(old_dl, new_dl, 'details refresh + anchors')

# ---------- M3/M10: remove duplicate legacy skill CSS; kill section-head .num print rule; dup lede rule; dup engage before ----------
must(""".skill-k { font-family: var(--sans); font-size: 10px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--euc); margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--rule-2); }
.skill-list { list-style: none; }
.skill-list li { font-family: var(--serif); font-size: 14.5px; line-height: 1.5; color: var(--cream-2); padding: 4px 0 4px 16px; position: relative; }
.skill-list li::before { content:''; position:absolute; left:0; top: 13px; width: 7px; height: 1px; background: var(--euc); }
.skill-list li:hover { color: var(--cream); }
""", "", 'legacy skill css block')

must("""  .section-head .num { font-size: 5.8pt; }
""", "", 'section-head num dead rule', 1)

must("""  .role-body p.lede { font-size: 6.6pt; line-height: 1.2; margin-bottom: 0.5px; display: none; }
  .role, .tile, .stat { break-inside: avoid; }""",
     """  .role, .tile, .stat { break-inside: avoid; }""", 'dup lede print rule')

must("""  .engage li::before { top: 1px; }
  .engage li::before { top: 0; }""",
     """  .engage li::before { top: 1px; }""", 'dup engage before')

# print: hide competency icons
must("  .engage li .engage-desc { display: none; }",
     """  .engage li .engage-desc { display: none; }
  .skill-icon { display: none !important; }""", 'print hide skill icons')

# ---------- M2: contrast raise ----------
must("  --cream-3: rgba(242,238,227,0.38);",
     "  --cream-3: rgba(242,238,227,0.55);", 'cream-3 contrast')

# ---------- M12: flags ----------
must('Executive Profile — Brisbane, Australia <span class="flag">🇦🇺</span>',
     'Executive Profile — Brisbane, Australia', 'eyebrow flag drop')
must('Brisbane, Australia <span class="flag">🇦🇺</span>',
     'Brisbane, Australia', 'contact flag drop')

# travel flags: local + alt=""
import re
def fixflag(m):
    code = m.group(1)
    return f'<img src="assets/flags/{code}.svg" alt="" loading="lazy"'
s2 = re.sub(r'<img src="https://raw\.githubusercontent\.com/HATScripts/circle-flags/gh-pages/flags/([a-z]{2})\.svg" alt="[^"]*"', fixflag, s)
flags_n = len(re.findall(r'assets/flags/', s2))
s = s2
print('travel flags localized:', flags_n)

# ---------- M13: nav blend -> scrim ----------
must("  mix-blend-mode: difference;",
     "  background: rgba(26,29,34,0.62);\n  backdrop-filter: blur(10px);\n  -webkit-backdrop-filter: blur(10px);", 'nav scrim')

# ---------- L6: aria on split hero ----------
must('<h1 data-kinetic>',
     '<h1 data-kinetic aria-label="Marcus Callon.">', 'h1 aria')
must('      <span class="ln"><span class="ch">M</span>',
     '      <span class="ln" aria-hidden="true"><span class="ch">M</span>', 'h1 ln1 aria')
must('      <span class="ln"><span class="ch">C</span>',
     '      <span class="ln" aria-hidden="true"><span class="ch">C</span>', 'h1 ln2 aria')
must('    <p class="thesis" data-thesis>',
     '    <p class="thesis" data-thesis aria-label="The translator across product, finance and architecture — an operator who leads with product, fluent in customer, P&L and code. Fractional & interim CXO mandates for founders & boards.">', 'thesis aria')
must('      <span class="ln"><span class="wd">The</span>',
     '      <span class="ln" aria-hidden="true"><span class="wd">The</span>', 'thesis ln1 aria')
must('      <span class="ln"><span class="wd">an</span>',
     '      <span class="ln" aria-hidden="true"><span class="wd">an</span>', 'thesis ln2 aria')
must('      <span class="ln"><span class="wd">Fractional</span>',
     '      <span class="ln" aria-hidden="true"><span class="wd">Fractional</span>', 'thesis ln3 aria')

open(p, 'w').write(s)
print('OK v10 canonical')
