# ============================================================
# CLIENTS & EMPLOYERS — grouped logo wall.
# "## Group name" starts a group.
# "- Name = style +"  -> the name rendered in the named style;
#   "+" marks it featured (fuller opacity). The used logo-name
#   also feeds the one-line print marquee.
# Styles: bbc / ft / mastercard / espn /
#         serif / serif-up / sans / sans-track
# ============================================================

# Display mode for the web logo wall:
#   style: words  - serif/sans wordmarks inline (the editorial-wall look)
#   style: marks  - uniform logomark tiles; org name appears on hover/focus
style: marks

# Print marquee (single line, shown only in the PDF) — order:
# display names as listed above, then this extra token.
marquee_extra: Wondaris

## Media & publishing
- BBC = bbc +
- the Guardian = serif
- ESPN = espn
- The Times = serif-up
- Financial Times = ft
- HEARST = sans-track

## Financial services
- Mastercard = mastercard +

## Insurance & listed
- RACQ = sans
- XPON = sans-track

## Government
- Queensland Transport = serif-up
- EQC = sans-track

## Ventures founded
- Shorthand = serif +
- Holoscribe = sans
- Immersive = serif
- FOCAL LABS = sans-track

## Education
- University of Otago = serif-up
