#!/usr/bin/env python3
"""Prune stale objects from an S3 bucket after a sync, skipping protected prefixes.

Usage:
  python3 scripts/prune_s3.py <bucket> <src-dir> [protected-prefix ...]

Environment:
  AWS_REGION                bucket region
  AWS_PROFILE               optional AWS CLI profile

Example:
  python3 scripts/prune_s3.py notorious.kiwi src archive/
"""

import json
import os
import subprocess
import sys
import tempfile

BUCKET = sys.argv[1]
SRC = sys.argv[2] if len(sys.argv) > 2 else 'src'
PROTECTED = sys.argv[3:] if len(sys.argv) > 3 else ['archive/']


def aws(*args):
    cmd = ['aws', '--region', os.environ.get('AWS_REGION', 'us-west-2')]
    if os.environ.get('AWS_PROFILE'):
        cmd += ['--profile', os.environ['AWS_PROFILE']]
    cmd += list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def list_s3_keys():
    out = aws('s3api', 'list-objects-v2', '--bucket', BUCKET)
    data = json.loads(out)
    return sorted(obj['Key'] for obj in data.get('Contents', []))


def list_src_keys():
    keys = set()
    for root, _dirs, files in os.walk(SRC, followlinks=True):
        for name in files:
            path = os.path.join(root, name)
            rel = os.path.relpath(path, SRC)
            keys.add(rel.replace(os.sep, '/'))
    return keys


def is_protected(key):
    return any(key.startswith(p) for p in PROTECTED)


def main():
    src_keys = list_src_keys()
    s3_keys = list_s3_keys()
    to_delete = [k for k in s3_keys if k not in src_keys and not is_protected(k)]

    if not to_delete:
        print('No stale S3 objects to prune.')
        return

    print(f'Pruning {len(to_delete)} stale object(s), protecting prefixes: {PROTECTED}')

    # delete-objects is limited to 1000 keys per request
    for i in range(0, len(to_delete), 1000):
        batch = to_delete[i:i + 1000]
        delete_doc = {'Objects': [{'Key': k} for k in batch]}

        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(delete_doc, f)
            tmp_path = f.name

        try:
            aws('s3api', 'delete-objects', '--bucket', BUCKET,
                '--delete', f'file://{tmp_path}')
        finally:
            os.unlink(tmp_path)

        print(f'  deleted batch of {len(batch)}')


if __name__ == '__main__':
    main()
