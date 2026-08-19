#!/usr/bin/env bash
# Deploy the generated src/ site to the S3 bucket for notorious.kiwi.
#
# Prerequisites:
#   - AWS CLI installed: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
#   - AWS credentials configured (default profile or AWS_PROFILE environment variable).
#
# Environment variables:
#   S3_BUCKET                   Target bucket (default: notorious.kiwi)
#   AWS_REGION                  Bucket region (default: us-west-2)
#   AWS_PROFILE                 AWS CLI profile to use
#   CLOUDFRONT_DISTRIBUTION_ID  Optional: distribution to invalidate after deploy

set -euo pipefail

BUCKET="${S3_BUCKET:-notorious.kiwi}"
REGION="${AWS_REGION:-us-west-2}"
PROFILE="${AWS_PROFILE:-}"
DIST_ID="${CLOUDFRONT_DISTRIBUTION_ID:-}"

aws_cmd() {
  if [ -n "$PROFILE" ]; then
    aws --profile "$PROFILE" --region "$REGION" "$@"
  else
    aws --region "$REGION" "$@"
  fi
}

echo "==> Verifying AWS credentials..."
aws_cmd sts get-caller-identity > /dev/null

echo "==> Syncing src/ to s3://$BUCKET/ ..."
aws_cmd s3 sync src/ "s3://$BUCKET/" --delete --no-progress

echo "==> Publishing profile.html as index.html ..."
aws_cmd s3 cp src/profile.html "s3://$BUCKET/index.html" --no-progress

if [ -n "$DIST_ID" ]; then
  echo "==> Invalidating CloudFront distribution $DIST_ID ..."
  if [ -n "$PROFILE" ]; then
    aws --profile "$PROFILE" cloudfront create-invalidation \
      --distribution-id "$DIST_ID" --paths "/*" >/dev/null
  else
    aws cloudfront create-invalidation \
      --distribution-id "$DIST_ID" --paths "/*" >/dev/null
  fi
fi

echo "==> Deployed to s3://$BUCKET/"
