set dotenv-load

export S3_BUCKET := env_var_or_default("S3_BUCKET", "notorious.kiwi")
export AWS_REGION := env_var_or_default("AWS_REGION", "us-west-2")

# Show available recipes when `just` is run with no arguments
_default:
    @just --list

# Build the website and variants
site:
    python3 scripts/build.py --variants

# Build the 2-page PDF (also rebuilds the site first)
pdf: site
    python3 scripts/build-print-direct.py
    rm -f v*-pdf-*.png print-pdf-*.png preview*.png

# Serve the built site locally (auto-opens in browser)
serve:
    python3 scripts/serve.py

# Build both site and PDF
all: pdf

# Deploy the built site to S3
deploy: site
    bash scripts/deploy.sh

# One-time S3/CloudFront bucket setup
deploy-setup:
    bash scripts/deploy-setup.sh
