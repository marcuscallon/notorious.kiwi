# Edit content/*.md, then run one of:

.PHONY: site pdf all deploy deploy-setup

site:
	python3 scripts/build.py --variants

pdf:
	python3 scripts/build.py --variants --pdf
	rm -f preview*.png
	node ~/.pi/agent/skills/pdf/scripts/html-to-pdf.mjs --file src/profile.html \
		-o Marcus-Callon-Executive-Profile.pdf --no-footer

all: pdf

deploy: site
	bash scripts/deploy.sh

deploy-setup:
	bash scripts/deploy-setup.sh
