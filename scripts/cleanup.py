"""Delete Firestore documents whose expireAt has passed (unpublished reviews, inactive profiles).

Runs daily from .github/workflows/cleanup.yml with a short-lived Google access token
(Workload Identity, no stored keys). Logs only counts, never personal data.

Usage: ACCESS_TOKEN=... python3 scripts/cleanup.py [--dry-run]
"""
import json, os, sys, urllib.request
from datetime import datetime, timezone

PROJECT = os.environ.get('FIREBASE_PROJECT', 'antarodaya-in')
BASE = f'https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents'
TOKEN = os.environ['ACCESS_TOKEN']
DRY_RUN = '--dry-run' in sys.argv


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read() or b'{}')


def expired(collection):
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    query = {'structuredQuery': {'from': [{'collectionId': collection}],
                                 'where': {'fieldFilter': {'field': {'fieldPath': 'expireAt'}, 'op': 'LESS_THAN',
                                                           'value': {'timestampValue': now}}},
                                 'limit': 500}}
    return [row['document']['name'] for row in call('POST', f'{BASE}:runQuery', query) if 'document' in row]


total = 0
for collection in ('reviews', 'users'):
    names = expired(collection)
    for name in names:
        if not DRY_RUN:
            call('DELETE', f'https://firestore.googleapis.com/v1/{name}')
    total += len(names)
    print(f'{collection}: {len(names)} expired document(s) {"found" if DRY_RUN else "deleted"}')
print(f'done: {total} total{" (dry run)" if DRY_RUN else ""}')
