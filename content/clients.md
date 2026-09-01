# ============================================================
# CLIENTS - grouped name/logo wall (marks mode).
# "## Group name" starts a group.
# "- Name = style +"  -> the name rendered in the named style;
#   "+" marks it featured (fuller opacity). Names also feed the
#   one-line print marquee (PDF).
# Styles: img:<file>,<mods>  - real logo from assets/clients/;
#           mods: chip (light-card backing) / invert (black art -> white) / wide (bigger box)
# Inline token: url:https://... makes the tile a link (web only; PDF stays text)
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
- BAFTA = img:bafta.png,chip url:https://www.bafta.org
- BBC = img:bbc.png url:https://www.bbc.com
- Blind Eye Films = img:blind-eye-films.png url:https://blindeyefilms.net
- Endemol = img:endemol.png,chip url:https://www.endemolshine.com
- ESPN = img:espn.png url:https://www.espn.com
- Hearst Magazines = img:hearst.png url:https://www.hearstmagazines.com
- The Financial Times = img:ft.png,chip,wide url:https://www.ft.com +
- The Global Mail = img:global-mail.png,invert url:https://en.wikipedia.org/wiki/The_Global_Mail
- The Guardian = img:guardian.png,invert url:https://www.theguardian.com
- The Times = img:the-times.png,invert url:https://www.thetimes.co.uk
- Trinity Mirror = img:trinity-mirror.png,invert url:https://reachplc.com
- Virgin Media = img:virgin-media.png url:https://www.virginmedia.com

## Charity, Non-Profit & Community
- Action Against Hunger = img:action-against-hunger.png url:https://www.actionagainsthunger.org
- Amnesty International = img:amnesty.png,chip url:https://www.amnesty.org
- Barnardos = img:barnardos.png,chip url:https://www.barnardos.org.au
- Inspire Education = img:inspire.png,chip url:https://inspireeducation.net.au
- Oxfam = img:oxfam.png url:https://www.oxfam.org
- Save the Children = img:save-the-children.png url:https://www.savethechildren.org.uk
- WaterAid = img:wateraid.png,chip url:https://www.wateraid.org

## Marketing, Technology & Telecommunications
- Bright Innovation = img:bright-innovation.png url:https://www.brightinnovation.co.uk
- Greenroom Digital = img:greenroom.png url:https://greenroomdigital.com.au
- Perform / Rapp Ltd = img:rapp.png,chip url:https://rapp.com

## Finance & Insurance
- AXA Insurance = img:axa.png url:https://www.axa.co.uk
- The Earthquake Commission NZ = img:eqc.png,chip url:https://www.eqc.govt.nz
- Mastercard = img:mastercard.png url:https://www.mastercard.com
- National Transport Insurance = img:nti.png url:https://www.nti.com.au
- RACQ = img:racq.png,chip url:https://www.racq.com.au

## Other
- Audi UK = img:audi.png,chip url:https://www.audi.co.uk
- Petronas = img:petronas.png url:https://www.petronas.com
- Queensland Transport = img:queensland-transport.png,chip url:https://www.tmr.qld.gov.au
- University of the Sunshine Coast (UniSC) = img:unisc.png,chip url:https://www.usc.edu.au
