#!/usr/bin/env python3
"""Build a dedicated print-only HTML and render the 2-page PDF.

This avoids mobile media-query leakage from the main web stylesheet.
"""
import os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SRC = os.path.join(ROOT, 'src', 'profile.html')
CSS = open(os.path.join(ROOT, 'scripts', 'print-layout.css')).read()

html = open(SRC).read()

# Replace the entire <style> block with our print-only stylesheet.
head_before, rest = html.split('<style>', 1)
_, head_after = rest.split('</style>', 1)

print_html = head_before + '<style>\n' + CSS + '\n</style>' + head_after
# Strip scripts so GSAP/Lenis/etc don't hide data-reveal elements before print.
print_html = re.sub(r'<script\b[^>]*>.*?</script>', '', print_html, flags=re.DOTALL)
print_html = re.sub(r'<script\b[^>]*/>', '', print_html, flags=re.DOTALL)
out_html = os.path.join(ROOT, 'src', 'profile-print.html')
open(out_html, 'w').write(print_html)

pdf = os.path.join(ROOT, 'Marcus-Callon-Executive-Profile.pdf')
cmd = [
    'node', os.path.expanduser('~/.pi/agent/skills/pdf/scripts/html-to-pdf.mjs'),
    '--file', out_html,
    '-o', pdf,
    '--no-footer'
]
print('Rendering print-only PDF...')
subprocess.run(cmd, check=True)
print('Wrote', pdf)
