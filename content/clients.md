# ============================================================
# CLIENTS - grouped name/logo wall (marks mode).
# "## Group name" starts a group.
# "- Name = style +"  -> the name rendered in the named style;
#   "+" marks it featured (fuller opacity). Names also feed the
#   one-line print marquee (PDF).
# Styles: img:<file>,<mods>  - real logo from assets/clients/;
#           mods: chip (light-card backing) / invert (black art -> white)
#         bbc / ft / mastercard / espn (hand-drawn glyphs)
#         serif / serif-up / sans / sans-track  (text, fallback; default: sans)
# ============================================================

# Display mode for the web wall:
#   style: words  - serif/sans wordmarks inline (the editorial-wall look)
#   style: marks  - uniform logomark tiles; org name appears on hover/focus
style: marks

# Display heading for the section (both web and print)
heading: Clients I've worked with

## Media, Publishing & Entertainment
- BAFTA = img:bafta.png,chip +
- BBC = img:bbc.png +
- Blind Eye Films = serif
- Endemol = img:endemol.png,chip
- ESPN = img:espn.png +
- Hearst Magazines = img:hearst.png
- The Financial Times = img:ft.png +
- The Global Mail = img:global-mail.png,invert
- The Guardian = img:guardian.png,invert
- The Times = img:the-times.png,invert
- Trinity Mirror = img:trinity-mirror.png,invert
- Virgin Media = img:virgin-media.png

## Charity, Non-Profit & Community
- Action Against Hunger = img:action-against-hunger.png +
- Amnesty International = img:amnesty.png,chip +
- Barnardos = img:barnardos.png,chip
- Inspire Education = img:inspire.png,chip
- Oxfam = img:oxfam.png +
- Save the Children = img:save-the-children.png
- St. Paul's Church = img:st-pauls.png,chip
- WaterAid = img:wateraid.png,chip

## Marketing, Technology & Telecommunications
- Bright Innovation = img:bright-innovation.png
- Greenroom Digital = img:greenroom.png
- Perform / Rapp Ltd = img:rapp.png,chip

## Finance & Insurance
- AXA Insurance = img:axa.png
- EQC = img:eqc.png,chip
- Mastercard = img:mastercard.png +
- NTI = img:nti.png
- RACQ = img:racq.png,chip

## Other
- Audi UK = img:audi.png,chip +
- Petronas = img:petronas.png
- Queensland Transport = serif-up
- University of the Sunshine Coast (UniSC) = img:unisc.png,chip
