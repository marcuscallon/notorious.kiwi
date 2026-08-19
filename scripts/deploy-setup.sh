#!/usr/bin/env bash
# One-time S3 bucket setup for static website hosting on notorious.kiwi.
# Run this once, then use make deploy for normal uploads.
#
# This configures:
#   - static website hosting (index.html / error.html)
#   - a public-read bucket policy
#
# Note: If you serve via CloudFront + HTTPS, use this in addition to (not
# instead of) your CloudFront distribution setup.

set -euo pipefail

BUCKET="${S3_BUCKET:-notorious.kiwi}"
REGION="${AWS_REGION:-us-west-2}"
PROFILE="${AWS_PROFILE:-}"

aws_cmd() {
  if [ -n "$PROFILE" ]; then
    aws --profile "$PROFILE" --region "$REGION" "$@"
  else
    aws --region "$REGION" "$@"
  fi
}

echo "==> Configuring static website hosting for s3://$BUCKET/ ..."
aws_cmd s3api put-bucket-website --bucket "$BUCKET" --website-configuration '{
  "IndexDocument": {"Suffix": "index.html"},
  "ErrorDocument": {"Key": "index.html"}
}'

echo "==> Applying public read bucket policy ..."
POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET/*"
    }
  ]
}
EOF
)
aws_cmd s3api put-bucket-policy --bucket "$BUCKET" --policy "$POLICY"

echo "==> Bucket configured."
echo "    S3 website endpoint: http://$BUCKET.s3-website-$REGION.amazonaws.com"
