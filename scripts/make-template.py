#!/usr/bin/env python3
"""One-off: split the current canonical profile.html into a template with
slot tokens, verifying every anchor exists. Slots are filled by build.py."""
import re, sys

s = open('src/profile.html').read()

def slot(s, start_marker, end_marker, token, greedy_ok=False):
    """Replace start..end(inclusive) with token."""
    a = s.find(start_marker)
    if a == -1:
        print(f'!! missing start marker for {token}: {start_marker[:70]}', file=sys.stderr); sys.exit(1)
    b = s.find(end_marker, a)
    if b == -1:
        print(f'!! missing end marker for {token}: {end_marker[:70]}', file=sys.stderr); sys.exit(1)
    b += len(end_marker)
    return s[:a] + token + s[b:]

# Hero name h1
s = slot(s, '    <h1 data-kinetic', '</h1>', '{{NAME}}')
# Thesis
s = slot(s, '    <p class="thesis"', '</p>', '{{THESIS}}')
# Contact
s = slot(s, '    <div class="contact" data-reveal>', '</div>', '{{CONTACT}}')
# Stats + spec: from stats div through the spec div close (just before hero section close)
s = slot(s, '    <div class="stats" data-reveal>', '    </div>\n  </section>', '{{HERO_FACTS}}\n  </section>')
# Stack tiles container contents: replace whole .stack div
a = s.find('    <div class="stack">')
b = s.find('\n    </div>\n  </section>', a)  # stack section close
assert a != -1 and b != -1
s = s[:a] + '{{STACK}}\n' + s[b + len('\n    </div>'):]
# Competencies grid
a = s.find('    <div class="skills-grid" data-reveal>')
b = s.find('\n    </div>\n  </section>', a)
assert a != -1 and b != -1
s = s[:a] + '{{COMPETENCIES}}\n' + s[b + len('\n    </div>'):]
# Clients details block
a = s.find('  <details class="signature-group clients-group" id="clients" open>')
b = s.find('\n  </details>', a); assert a != -1 and b != -1
s = s[:a] + '{{CLIENTS}}' + s[b + len('\n  </details>')+1:]
# Roles: from first role div to before the earlier block
a = s.find('    <div class="role" data-reveal>')
earlier_a = s.find('    <div class="earlier" data-reveal>')
assert a != -1 and earlier_a != -1
s = s[:a] + '{{ROLES}}\n\n' + s[earlier_a:]
# earlier rows: keep the .earlier wrapper + cn-k head, slot the rows
ea = s.find('<div class="earlier" data-reveal>')
il = s.find('<div class="earlier-row">', ea)
assert ea != -1 and il != -1
ie = s.find('\n    </div>\n\n    <div class="earlier"', il)
s2 = s.find('\n  </section>', il)
assert s2 != -1
# rows end at the section close div for .earlier
ron = s.find('  </section>', il)
# the .earlier div closes right before section close
divclose = s.rfind('</div>', il, ron)
s = s[:il] + '{{EARLIER_ROWS}}\n    ' + s[divclose:]
a = s.find('    <ul>\n      <li data-reveal><strong>Fractional')
b = s.find('    </ul>', a); assert a != -1 and b != -1
s = s[:a] + '{{ENGAGE_UL}}' + s[b + len('    </ul>')+1:]
# Signature details block
a = s.find('  <details class="signature-group">')
b = s.find('\n  </details>', a); assert a != -1 and b != -1
s = s[:a] + '{{SIGNATURE}}' + s[b + len('\n  </details>')+1:]
# Footer contents
a = s.find('  <footer class="foot">')
b = s.find('\n  </footer>', a); assert a != -1 and b != -1
s = s[:a] + '{{FOOTER}}' + s[b + len('\n  </footer>')+1:]

open('template.html', 'w').write(s)
print('template.html written with slots:')
for t in ['NAME','THESIS','CONTACT','HERO_FACTS','STACK','COMPETENCIES','CLIENTS','ROLES','EARLIER_ROWS','ENGAGE_UL','SIGNATURE','FOOTER']:
    ok = '{{' + t + '}}' in s
    print(('  ok  ' if ok else '  MISS') , t)
    if not ok: sys.exit(1)
